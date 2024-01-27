from dateutil.parser import parse
from pydantic import BaseModel, conint, conlist, constr, validator


from typing import Optional
from datetime import datetime

class CustomDateTimeModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
        }

class RepoModel(CustomDateTimeModel):
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
    created_at: str
    pushed_at: str
    stargazers_count: conint(ge=0)
    # language is an array of strings or None
    language: Optional[constr(min_length=1)] = None

    @validator('created_at', 'pushed_at')
    def parse_date(cls, v):
        return parse(v)

    @validator('topics', pre=True, always=True)
    def convert_topics(cls, value):
        return [topic.lower() for topic in value]
    

"""
example_data = {
    "full_name": "cbovis/awesome-digital-nomads",
    "description": "🏝 A curated list of awesome resources for Digital Nomads.",
    "topics": [
        "awesome",
        "awesome-list",
        "digital-nomad",
        "digital-nomads",
        "nomad",
        "remote-work"
    ],
    "created_at": "2017-02-02T07:12:11Z",
    "pushed_at": "2023-05-03T15:27:59Z",
    "stargazers_count": 798,
    "language": "python"
}
"""    