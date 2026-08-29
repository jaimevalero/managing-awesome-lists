from dateutil.parser import parse
from pydantic import BaseModel, conint, conlist, constr, field_validator


from typing import Optional
from datetime import datetime

class RepoModel(BaseModel):
    """
    Model for storing metadata of a repository.

    Attributes:
        full_name (str): Full name of the repository.
        description (str): Description of the repository.
        topics (list[str]): List of topics of the repository.
        created_at (datetime): Creation date of the repository.
        pushed_at (datetime): Date of the last update of the repository.
        stargazers_count (int): Number of stars of the repository.
        language (str): Main language of the repository.
    """
    full_name: str
    description: str
    topics: conlist(str)
    created_at: datetime
    pushed_at: datetime
    stargazers_count: conint(ge=0)
    # language is an array of strings or None
    language: Optional[constr(min_length=1)] = None

    @field_validator('created_at', 'pushed_at', mode='before')
    @classmethod
    def parse_date(cls, v):
        return parse(v) if isinstance(v, str) else v

    @field_validator('topics', mode='before')
    @classmethod
    def convert_topics(cls, value):
        return [topic.lower() for topic in value]

