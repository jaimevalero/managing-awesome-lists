from loguru import logger
from abc import ABC, abstractmethod
from typing import List
from src.helpers.RepoModelList import delete_duplicates, sort_by_star
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer

from src.models.RepoModel import RepoModel

class AbstractPopulator(ABC):
    """ Abstract class for populating a list of repos, based on 
     - a list of awesome lists
     - a list of topics """



    def __init__(self, access_token,name):
        self.name = name
        self.access_token = access_token
        self.repos_data = None
        self.current_index = 0  # Añade un índice para seguir la iteración

    def __enter__(self):
        # Aquí puedes poner cualquier código de configuración que necesites.
        return self.populate()

    def __iter__(self):
        return iter(self.repos_data)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Aquí puedes poner cualquier código de limpieza que necesites.
        # Si se produjo una excepción, sus detalles se pasan como argumentos a este método.
        pass

    def __next__(self):
        if self.current_index >= len(self.repos_data):
            raise StopIteration
        result = self.repos_data[self.current_index]
        self.current_index += 1
        return result

    def populate(self)->List[RepoModel]:
        raise NotImplementedError("Please Implement this method")
    
    def normalize(self, repos_data: List[RepoModel])->List[RepoModel]:
        """ Normalize the data from the repos """
        repos_data=sort_by_star(repos_data)
        repos_data=delete_duplicates(repos_data)
        return repos_data
    