from pydantic import BaseModel
from typing import List
from src.models.RepoModel import RepoModel

class AbstractModel(BaseModel):
    """ This Base class is for serializing a category
    """
    category_type: str
    category_name: str
    repo_list_models: List[RepoModel]
    frecuent_topics: dict
    
    class Config:
        arbitrary_types_allowed = True