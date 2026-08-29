from typing import ClassVar, List, Optional

from pydantic import BaseModel, constr


class SimilarRepoModel(BaseModel):
    """ Model for one repo shown as similar to another one.

    It carries a copy of the few fields the frontend paints in the "similar repos"
    popover, so that showing them does not mean loading the other repos.

    Attributes:
        full_name (str): Full name of the similar repository.
        description (str): What the repo does, shown when hovering the suggestion. Cut
            short on purpose: it is a tooltip, and it is copied into 25.000 files.
        stargazers_count (int): Number of stars, used to break ties between repos that
            are equally similar: the abandoned clone should not outrank the real one.
        language (str): Main language of the similar repository.
        shared_topics (list[str]): Topics both repos have in common. Shown as the reason
            why they are similar, which is what makes the suggestion trustworthy.
    """
    # ClassVar, si no pydantic lo tomaria por un campo mas del modelo
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 140

    full_name: str
    description: str = ''
    stargazers_count: int
    language: Optional[constr(min_length=1)] = None
    shared_topics: List[str] = []
