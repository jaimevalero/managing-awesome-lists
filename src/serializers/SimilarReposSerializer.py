
import json
from typing import List

from src.helpers.RepoModelList import get_frecuent_topics
from src.models.RepoModel import RepoModel
from src.models.SimilarRepoModel import SimilarRepoModel
from src.models.SimilarReposModel import SimilarReposModel
from src.serializers.AbstractSerializer import AbstractSerializer


class SimilarReposSerializer(AbstractSerializer):
    """
    A subclass of AbstractSerializer that serializes the repos similar to a given repo.

    One file per repo is written to "./var/similar", named after the repo with '/' replaced
    by '@', the same convention as the other serializers. One file per repo and not a single
    index because the frontend only shows similar repos when the reader asks for them on one
    card: it fetches that one file, a couple of kilobytes, instead of a table of 25.000 repos.

    The directory has to be called like SimilarReposModel.category_type, because the generic
    frontend route /a-<type>/<name> fetches /<type>/<name>.json.

    Repos with nothing similar enough get no file at all, which is how the frontend knows
    not to offer the option there.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. In this case, it's "similar".

    Methods
    -------
    to_file(repo: RepoModel, similar: List[SimilarRepoModel])
        Serializes the similar repos of the given repo to a .json file.
    from_file(full_name: str) -> SimilarReposModel
        Deserializes the similar repos of the given repo.
    """

    CATEGORY = "similar"

    @staticmethod
    def to_file(repo: RepoModel, similar: List[SimilarRepoModel]):
        similar_repos = SimilarReposModel(
            category_type=SimilarReposSerializer.CATEGORY,
            category_name=repo.full_name,
            repos_data=similar,
            frecuent_topics=get_frecuent_topics(similar),
            repo_meta_data=repo)
        filename_clean = repo.full_name.replace('/', '@')
        object_serialized_path = f"./var/{SimilarReposSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
            f.write(similar_repos.model_dump_json())

    @staticmethod
    def from_file(full_name: str) -> SimilarReposModel:
        filename_clean = full_name.replace('/', '@')
        with open(f"./var/{SimilarReposSerializer.CATEGORY}/{filename_clean}.json") as f:
            return SimilarReposModel(**json.load(f))
