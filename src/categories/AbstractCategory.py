from typing import List

from src.serializers.RepoSerializer import AbstractSerializer
from src.populators.AbstractPopulator import AbstractPopulator
from src.models.RepoModel import RepoModel  
from abc import ABC


class AbstractCategory(ABC):
    category_type: str     # category_type only can be "awesome" or "topic"
    category_name: str     # category_name is the name of the category
    repo_meta_data: RepoModel  # attribute for metadata of this repo
    access_token :str      # access_token for github api
    repo_list_names: List[str]  
    repos_data: List[RepoModel]  
    populator: AbstractPopulator
    serializer: AbstractSerializer
    
    def __init__(self, category_name: str, access_token: str):
        self.category_name = category_name
        self.access_token = access_token
        self.repo_list_names = []
        self.repos_data = self.populator(self.access_token, self.category_name)
    