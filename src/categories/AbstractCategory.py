from typing import List
from src.helpers.RepoModelList import get_frecuent_topics

from src.serializers.AbstractSerializer import AbstractSerializer
from src.populators.AbstractPopulator import AbstractPopulator
from src.models.RepoModel import RepoModel  
from abc import ABC
from loguru import logger

class AbstractCategory(ABC):
    """
    An abstract base class that represents a category of repositories.

    This class provides a structure for storing information about a category of repositories,
    including the category type and name, metadata about the repository, an access token for the GitHub API,
    a list of repository names, data about the repositories, a populator, a serializer, and frequent topics.

    Attributes
    ----------
    category_type : str
        The type of the category, which can only be "awesome" or "topic".
    category_name : str
        The name of the category.
    repo_meta_data : RepoModel
        Metadata about the repository.
    access_token : str
        An access token for the GitHub API.
    repo_list_names : List[str]
        A list of repository names.
    repos_data : List[RepoModel]
        Data about the repositories.
    populator : AbstractPopulator
        A populator object.
    serializer : AbstractSerializer
        A serializer object.
    frecuent_topics : dict
        A dictionary of frequent topics.

    Methods
    -------
    __init__(self, category_name: str, access_token: str)
        Initializes the AbstractCategory with the given category name and access token.
    get_frecuent_topics(self, repo_list_models: List[RepoModel])
        Returns a dictionary of frequent topics from the given list of RepoModel objects.
    """
    ...    
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
            