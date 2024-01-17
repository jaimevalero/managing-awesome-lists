from typing import List
from src.helpers.RepoModelList import get_frecuent_topics
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer

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
    category_name: str     # category_name is the name of the category, or the repo name
    repo_meta_data: RepoModel  # attribute for metadata of this repo
    access_token :str      # access_token for github api
    repo_list_names: List[str]  # List of repo names
    repos_data: List[RepoModel]  # List of repo metadata
    populator: AbstractPopulator    # Class to populate the data for the instance
    serializer: AbstractSerializer  # Class to serialize the data for the instance
    frecuent_topics: dict   # Dict counter of most frecuent topics for the repos 
    
    def __init__(self, category_name: str, access_token: str, populator, serializer):
        self.category_name = category_name
        self.access_token = access_token
        self.populator = populator
        self.serializer = serializer
        self.repo_list_names = []
        self.repos_data = self.populator(self.access_token, self.category_name).populate()
        self.frecuent_topics = self.get_frecuent_topics(self.repos_data)

    def get_frecuent_topics(self,repos_data):
        try : 
            frecuent_topics = get_frecuent_topics(repos_data)
            self.frecuent_topics = frecuent_topics
            return self.frecuent_topics
        except Exception as e:
            logger.exception(f"Error with {repos_data} {e}")   
            return {}

    def to_file(self):
        self.serializer.to_file(self)

    def __del__(self):
        """ Serialize the data from the repos when the object is deleted """
        self.to_file()
        self.serialize_repo_data()

    def serialize_repo_data(self):
        """ Serialize the repo data to a file """
        for repo_data in self.repos_data:
            RepoMetaDataSerializer.to_file(repo_data)  

