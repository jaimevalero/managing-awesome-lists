from pydantic import BaseModel
from typing import List
from src.models.AbtractModel import AbstractModel
from src.models.RepoModel import RepoModel

class AwesomeModel(AbstractModel):
    """ This class is for serializing the awesome list only
    """
    repo_meta_data: RepoModel