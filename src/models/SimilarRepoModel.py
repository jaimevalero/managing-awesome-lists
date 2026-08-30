from datetime import datetime
from typing import ClassVar, List, Optional

from dateutil.parser import parse
from pydantic import BaseModel, constr, field_validator


class SimilarRepoModel(BaseModel):
    """ Model for one repo shown as similar to another one.

    It carries a copy of the fields the frontend paints for a repo, so that showing a
    neighbour does not mean loading its own file. That copy is what lets the page of
    similar repos reuse the generic category page -- with its search, its Hot/Top/New
    order and its pagination -- without a line of frontend code.

    The description is the only field that is not copied whole: it is a tooltip, and it
    is duplicated across 25.000 files.

    What is deliberately NOT here is the list of topics shared with the origin repo.
    It used to be stored, but now that the full topic list travels with each neighbour
    it is just the intersection of two lists the browser already has, and storing a
    derived value in 25.000 files is 13 MB of a second source of truth.

    Attributes:
        full_name (str): Full name of the similar repository.
        description (str): What the repo does, shown when hovering the suggestion. Cut
            short on purpose: it is a tooltip, and it is copied into 25.000 files.
        stargazers_count (int): Number of stars, used to break ties between repos that
            are equally similar: the abandoned clone should not outrank the real one.
        language (str): Main language of the similar repository.
        topics (list[str]): Its topics. Painted on the card, and intersected with the
            origin's to explain why the two repos are similar.
        created_at (datetime): Creation date. Not optional: the Hot and New orders of
            the similar-repos page are computed from it.
        pushed_at (datetime): Date of the last push, shown on the card and used by the
            Recently updated order.
    """
    # ClassVar, si no pydantic lo tomaria por un campo mas del modelo
    MAX_DESCRIPTION_LENGTH: ClassVar[int] = 140

    full_name: str
    description: str = ''
    stargazers_count: int
    language: Optional[constr(min_length=1)] = None
    topics: List[str] = []
    created_at: datetime
    pushed_at: datetime

    @field_validator('created_at', 'pushed_at', mode='before')
    @classmethod
    def parse_date(cls, v):
        return parse(v) if isinstance(v, str) else v
