from pydantic import BaseModel
from typing import List
from src.models.RepoModel import RepoModel

class AwesomeModel(BaseModel):
    """ This class is for serializing the awesome list only
    """
    category_type: str
    category_name: str
    repo_meta_data: RepoModel
    repo_list_models: List[RepoModel]

    class Config:
        arbitrary_types_allowed = True