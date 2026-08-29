
import math
import re
from collections import Counter, defaultdict
from typing import List

import numpy as np
from loguru import logger

from src.models.RepoModel import RepoModel
from src.models.SimilarRepoModel import SimilarRepoModel


class RepoSimilarity:
    """
    Finds, for a given repo, the repos most similar to it inside a list of repos.

    Similarity is computed from the metadata already downloaded for every repo (topics,
    description and language), so finding similar repos costs no extra request to github
    and no readme to download. Each repo becomes a vector of weighted features and two
    repos are as similar as the cosine between their vectors.

    Two repos can talk about the same thing without sharing a single word, so optionally
    a second opinion is used: the embeddings from EmbeddingDownloader, which do find that
    ripgrep and the_silver_searcher are the same kind of tool. The two signals disagree in
    a useful way, vocabulary is precise and embeddings recall more, so a repo is suggested
    when either of them is convinced (each has its own threshold) and the final order is
    decided by fusing both rankings. Their scores are not comparable as numbers, an
    embedding cosine of 0.65 is mediocre while a vocabulary cosine of 0.65 is excellent,
    which is why positions are fused instead of scores.

    Every feature is weighted by its inverse document frequency, so that sharing a rare
    topic ("linenoise") counts and sharing a topic half of github uses ("hacktoberfest")
    does not. Topics weigh more than description words because they are curated by the
    author, and the description is only a line of prose that may not even mention what
    the repo does.

    Comparing every repo against every other one would be 25.000 x 25.000 comparisons, so
    an inverted index gives, for each repo, only the repos that share at least one feature
    with it. Features present in too many repos are skipped when building that index (they
    would return a third of github as candidates) but still count when scoring.

    Attributes
    ----------
    MAX_RESULTS : int
        How many similar repos are kept per repo. Beyond a handful it stops being a
        suggestion and becomes another list to read.
    MIN_SCORE, MIN_EMBEDDING_SCORE : float
        Similarity below this, for each signal, is not shown at all. A "similar repos"
        section that sometimes shows junk teaches people to ignore it for good.
    EMBEDDING_CANDIDATES : int
        How many nearest neighbours by embedding enter the candidate list of each repo.
    MAX_DOCUMENT_FREQUENCY : float
        Fraction of the repos above which a feature is too common to look candidates up by.
    DESCRIPTION_WEIGHT, LANGUAGE_WEIGHT : float
        Weight of a description word and of the language, relative to a topic.

    Methods
    -------
    most_similar(repo: RepoModel) -> List[SimilarRepoModel]
        The repos most similar to the given one, best first, empty if none is similar
        enough.
    """

    MAX_RESULTS = 5
    MIN_SCORE = 0.3
    MIN_EMBEDDING_SCORE = 0.65
    EMBEDDING_CANDIDATES = 20
    # Rank fusion constant: how much a first position is worth over a second one. 60 is
    # the usual value, high enough that no single signal decides the whole order
    RANK_FUSION_CONSTANT = 60
    # Popularity is the third, weaker voice in that fusion: it should reorder repos that
    # are similarly relevant, never promote an unrelated repo for being popular
    POPULARITY_WEIGHT = 0.5
    MAX_DOCUMENT_FREQUENCY = 0.02
    DESCRIPTION_WEIGHT = 0.35
    LANGUAGE_WEIGHT = 0.5

    # Words of 3 characters or more, keeping the ones that carry meaning in this domain
    # (c++, node.js, gpt-4). Shorter tokens are noise once the weighting is done.
    WORD = re.compile(r'[a-z0-9][a-z0-9+#.-]{2,}')

    def __init__(self, repo_list: List[RepoModel], embeddings=None):
        self.repo_list = repo_list
        self.embeddings = embeddings
        self.vectors = self.__build_vectors(repo_list)
        self.index = self.__build_index()
        self.positions = {repo.full_name: position for position, repo in enumerate(repo_list)}

    def most_similar(self, repo: RepoModel) -> List[SimilarRepoModel]:
        position = self.positions.get(repo.full_name)
        if position is None:
            return []

        vocabulary_scores = self.__score_candidates(position)
        embedding_scores = self.__score_by_embedding(position)
        candidates = {
            candidate for candidate, score in vocabulary_scores.items() if score >= RepoSimilarity.MIN_SCORE
        } | {
            candidate for candidate, score in embedding_scores.items() if score >= RepoSimilarity.MIN_EMBEDDING_SCORE
        }
        if not candidates:
            return []

        return self.__best_results(repo, self.__fuse_rankings(candidates, vocabulary_scores, embedding_scores))

    def __best_results(self, repo: RepoModel, best: list) -> List[SimilarRepoModel]:
        """ The first results, keeping only one repo per name.

        Two repos with the same name (Picocrypt/Picocrypt and HACKERALERT/Picocrypt) are
        the same project living in two places, a mirror or a fork, and deduplication does
        not merge them because github says they are different repos. They are still the
        same suggestion, and there are only five slots.
        """
        results, seen_names = [], {repo.full_name.split('/')[-1].lower()}
        for candidate in best:
            name = self.repo_list[candidate].full_name.split('/')[-1].lower()
            if name in seen_names:
                continue
            seen_names.add(name)
            results.append(self.__as_similar_repo(repo, candidate))
            if len(results) == RepoSimilarity.MAX_RESULTS:
                break
        return results

    def __fuse_rankings(self, candidates: set, vocabulary_scores: dict, embedding_scores: dict) -> list:
        """ Orders the candidates by their position in each signal instead of by score.

        Popularity votes too, with less weight: an abandoned clone and the repo everybody
        actually uses look equally similar to both signals, and suggesting the clone first
        is how a "similar repos" section loses the reader's trust.
        """
        stars = {candidate: float(self.repo_list[candidate].stargazers_count) for candidate in candidates}
        fused = defaultdict(float)
        for scores, weight in ((vocabulary_scores, 1.0), (embedding_scores, 1.0), (stars, RepoSimilarity.POPULARITY_WEIGHT)):
            ranked = sorted(candidates, key=lambda candidate: -scores.get(candidate, 0.0))
            for rank, candidate in enumerate(ranked):
                if scores.get(candidate, 0.0) > 0:
                    fused[candidate] += weight / (RepoSimilarity.RANK_FUSION_CONSTANT + rank)
        return sorted(fused, key=lambda candidate: (-fused[candidate], -stars[candidate]))

    def __as_similar_repo(self, repo: RepoModel, candidate: int) -> SimilarRepoModel:
        similar = self.repo_list[candidate]
        return SimilarRepoModel(
            full_name=similar.full_name,
            stargazers_count=similar.stargazers_count,
            language=similar.language,
            shared_topics=sorted(set(repo.topics) & set(similar.topics)))

    def __score_by_embedding(self, position: int) -> dict:
        """ The nearest neighbours of a repo in the embedding space, empty when ollama was
        not available and the pipeline ran without embeddings """
        if self.embeddings is None:
            return {}
        similarities = self.embeddings @ self.embeddings[position]
        similarities[position] = -1.0
        nearest = np.argpartition(-similarities, RepoSimilarity.EMBEDDING_CANDIDATES)[:RepoSimilarity.EMBEDDING_CANDIDATES]
        return {int(candidate): float(similarities[candidate]) for candidate in nearest}

    def __score_candidates(self, position: int) -> dict:
        """ Cosine similarity against every repo sharing at least one feature """
        scores = defaultdict(float)
        for feature, weight in self.vectors[position].items():
            for candidate in self.index.get(feature, ()):
                if candidate != position:
                    scores[candidate] += weight * self.vectors[candidate][feature]
        return scores

    def __build_vectors(self, repo_list: List[RepoModel]) -> List[dict]:
        features = [self.__features(repo) for repo in repo_list]
        self.document_frequency = Counter(feature for repo_features in features for feature in repo_features)
        total = len(repo_list) or 1
        inverse_document_frequency = {
            feature: math.log(total / frequency) for feature, frequency in self.document_frequency.items()
        }

        vectors = []
        for repo_features in features:
            vector = {
                feature: weight * inverse_document_frequency[feature]
                for feature, weight in repo_features.items()
            }
            # Normalized, so that a repo with many topics is not similar to everything
            length = math.sqrt(sum(weight * weight for weight in vector.values())) or 1.0
            vectors.append({feature: weight / length for feature, weight in vector.items()})
        logger.info(f"Built {len(vectors)} repo vectors out of {len(inverse_document_frequency)} features")
        return vectors

    def __features(self, repo: RepoModel) -> dict:
        """ The weighted features of a repo, prefixed so that a topic and a word of the
        description that happen to be the same string do not count twice """
        features = {feature: 1.0 for feature in (f"topic:{topic}" for topic in repo.topics)}
        for word in set(RepoSimilarity.WORD.findall((repo.description or '').lower())):
            features.setdefault(f"word:{word}", RepoSimilarity.DESCRIPTION_WEIGHT)
        if repo.language:
            features[f"language:{repo.language.lower()}"] = RepoSimilarity.LANGUAGE_WEIGHT
        return features

    def __build_index(self) -> dict:
        max_document_frequency = len(self.repo_list) * RepoSimilarity.MAX_DOCUMENT_FREQUENCY
        index = defaultdict(list)
        for position, vector in enumerate(self.vectors):
            for feature in vector:
                if self.document_frequency[feature] <= max_document_frequency:
                    index[feature].append(position)
        return index
