from pydantic import BaseModel, ConfigDict
from typing import List
from src.models.RepoModel import RepoModel

class AbstractModel(BaseModel):
    """ This Base class is for serializing a category
    """
    category_type: str
    category_name: str
    repos_data: List[RepoModel]
    frecuent_topics: dict
    
    model_config = ConfigDict(arbitrary_types_allowed=True)