
import json
from typing import List

from src.models.RelatedReposModel import RelatedReposModel
from src.models.SimilarRepoModel import SimilarRepoModel
from src.serializers.AbstractSerializer import AbstractSerializer


class RelatedReposSerializer(AbstractSerializer):
    """
    A subclass of AbstractSerializer that serializes the repos similar to a given repo.

    One file per repo is written to "./var/related", named after the repo with '/' replaced
    by '@', the same convention as the other serializers. One file per repo and not a single
    index because the frontend only shows similar repos when the reader asks for them on one
    card: it fetches that one file, a few hundred bytes, instead of a table of 25.000 repos.

    Repos with nothing similar enough get no file at all, which is how the frontend knows
    not to offer the option there.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. In this case, it's "related".

    Methods
    -------
    to_file(full_name: str, related: List[SimilarRepoModel])
        Serializes the similar repos of the given repo to a .json file.
    from_file(full_name: str) -> RelatedReposModel
        Deserializes the similar repos of the given repo.
    """

    CATEGORY = "related"

    @staticmethod
    def to_file(full_name: str, related: List[SimilarRepoModel]):
        related_repos = RelatedReposModel(full_name=full_name, related=related)
        filename_clean = full_name.replace('/', '@')
        object_serialized_path = f"./var/{RelatedReposSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
            f.write(related_repos.model_dump_json())

    @staticmethod
    def from_file(full_name: str) -> RelatedReposModel:
        filename_clean = full_name.replace('/', '@')
        with open(f"./var/{RelatedReposSerializer.CATEGORY}/{filename_clean}.json") as f:
            return RelatedReposModel(**json.load(f))
