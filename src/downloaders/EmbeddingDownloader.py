
from typing import List

import numpy as np
import requests
from loguru import logger

from src.models.RepoModel import RepoModel


class EmbeddingDownloader:
    """
    Downloads the embeddings of a list of repos from a local ollama.

    An embedding places a repo in a space where distance means "talks about the same
    thing", which finds neighbours that share no word at all: ripgrep and the_silver_searcher,
    or age and Picocrypt. It complements the vocabulary matching of RepoSimilarity, which
    is the other way around: precise when two repos share topics, blind when they do not.

    Nothing is downloaded from github here, the text embedded is the metadata already
    cached in ./var/repo, so no readme is ever fetched.

    Ollama is optional: if it is not running the pipeline goes on without embeddings and
    the similarity falls back to vocabulary only, because a monthly batch should not fail
    because a local service is down.

    Attributes
    ----------
    MODEL : str
        Ollama model used. nomic-embed-text is small and fast, and these texts are in
        english. It needs the "search_document: " prefix its authors trained it with,
        without it the results degrade badly.
    BATCH_SIZE : int
        Repos per request. Ollama is much faster in batches than one by one.

    Methods
    -------
    download(repo_list: List[RepoModel]) -> np.ndarray
        A matrix with one normalized embedding per repo, or None if ollama is unreachable.
    """

    API_URL = 'http://localhost:11434/api/embed'
    MODEL = 'nomic-embed-text:latest'
    DOCUMENT_PREFIX = 'search_document: '
    BATCH_SIZE = 128
    TIMEOUT = 600

    @staticmethod
    def download(repo_list: List[RepoModel]):
        texts = [EmbeddingDownloader.__as_text(repo) for repo in repo_list]
        embeddings = []
        for start in range(0, len(texts), EmbeddingDownloader.BATCH_SIZE):
            batch = texts[start:start + EmbeddingDownloader.BATCH_SIZE]
            try:
                response = requests.post(
                    EmbeddingDownloader.API_URL,
                    json={'model': EmbeddingDownloader.MODEL, 'input': batch},
                    timeout=EmbeddingDownloader.TIMEOUT)
                response.raise_for_status()
                embeddings.extend(response.json()['embeddings'])
            except Exception as e:
                logger.warning(f"Could not get embeddings from ollama, similarity will use vocabulary only: {e}")
                return None
            if start and not start % (EmbeddingDownloader.BATCH_SIZE * 50):
                logger.info(f"Embedded {start}/{len(texts)} repos")

        matrix = np.array(embeddings, dtype=np.float32)
        # Normalized once here, so that comparing two repos is just a dot product
        matrix /= np.linalg.norm(matrix, axis=1, keepdims=True).clip(min=1e-9)
        logger.info(f"Embedded {len(matrix)} repos in {matrix.shape[1]} dimensions")
        return matrix

    @staticmethod
    def __as_text(repo: RepoModel) -> str:
        """ The name is included on purpose: for repos with no description it is the only
        thing left, and it usually says what the repo is (awesome-selfhosted, yt-dlp) """
        return (f"{EmbeddingDownloader.DOCUMENT_PREFIX}{repo.full_name} "
                f"{repo.description} {' '.join(repo.topics)} {repo.language or ''}")
