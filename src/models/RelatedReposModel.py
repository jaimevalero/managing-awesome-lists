from typing import List

from pydantic import BaseModel

from src.models.SimilarRepoModel import SimilarRepoModel


class RelatedReposModel(BaseModel):
    """ This class is for serializing the repos similar to a given repo.

    One of these is written per repo, so the frontend can fetch just the neighbours of
    the repo the user asked about instead of a table of all of them.

    Attributes:
        full_name (str): Full name of the repository these are similar to.
        related (list[SimilarRepoModel]): Its most similar repos, best first.
    """
    full_name: str
    related: List[SimilarRepoModel]
