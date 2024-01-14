from typing import List
from src.helpers.RepoModelList import get_frecuent_topics

from src.serializers.AbstractSerializer import AbstractSerializer
from src.populators.AbstractPopulator import AbstractPopulator
from src.models.RepoModel import RepoModel  
from abc import ABC
from loguru import logger

class AbstractCategory(ABC):
    category_type: str     # category_type only can be "awesome" or "topic"
    category_name: str     # category_name is the name of the category
    repo_meta_data: RepoModel  # attribute for metadata of this repo
    access_token :str      # access_token for github api
    repo_list_names: List[str]  
    repos_data: List[RepoModel]  
    populator: AbstractPopulator
    serializer: AbstractSerializer
    frecuent_topics: dict
    
    def __init__(self, category_name: str, access_token: str):
        self.category_name = category_name
        self.access_token = access_token
        self.repo_list_names = []
        self.repos_data = self.populator(self.access_token, self.category_name)
        
    def get_frecuent_topics(self,repo_list_models):
        try : 
            frecuent_topics = get_frecuent_topics(repo_list_models)
            self.frecuent_topics = frecuent_topics
            return self.frecuent_topics
        except Exception as e:
            logger.exception(f"Error with {repo_list_models} {e}")   
            return {}
            