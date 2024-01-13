#from src.categories.AbstractCategory import AbstractCategory
#from src.categories.AwesomeCategory import AwesomeCategory
from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel        


import json
import os

class AbstractSerializer:
    CATEGORY = None

    @staticmethod
    def exists_file(repo_name:str,category) -> bool:
        filename = repo_name.replace('/', '@')
        return os.path.isfile(f"./var/{category}/{filename}.json")


    @staticmethod
    def to_file(object):
        pass

    @staticmethod
    def from_file(name: str) -> RepoModel:
        pass

class TopicSerializer(AbstractSerializer):
     pass

class AwesomeSerializer(AbstractSerializer):
    CATEGORY = "awesome"
    @staticmethod
    def to_file(awesome_category):
        
        repo_meta_data = awesome_category.repo_meta_data
        awesome_model = AwesomeModel(
            category_type=awesome_category.category_type,
            category_name=awesome_category.category_name,
            repo_meta_data=awesome_category.repo_meta_data,
            repo_list_models=awesome_category.repo_list_models
        )        
        filename_clean = repo_meta_data.full_name.replace('/', '@')

        
        object_serialized_path = f"./var/{AwesomeSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
                    f.write(awesome_model.model_dump_json())
        
class RepoMetaDataSerializer(AbstractSerializer):
    """
    Class for serializing and deserializing instances of RepoMetaData to and from a file.

    Methods:
        to_file(repo_meta_data: RepoMetaData, filename: str): Saves an instance of RepoMetaData to a file.
        from_file(filename: str) -> RepoMetaData: Loads an instance of RepoMetaData from a file.
    """
    CATEGORY = "repo"


    @staticmethod
    def to_file(repo_meta_data: RepoModel):
        filename_clean = repo_meta_data.full_name.replace('/', '@')
        # Overwrite the file if it already exists
        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename_clean}.json", 'w') as f:
                    f.write(repo_meta_data.model_dump_json())


    @staticmethod
    def from_file(repo_name: str) -> RepoModel:
        filename = repo_name.replace('/', '@')

        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename}.json") as f:
            data = json.load(f)
        return RepoModel(**data)
    
    @staticmethod
    def exists_file(repo_name:str) -> bool:
        # We invoke the static method from the parent class
        return AbstractSerializer.exists_file(repo_name,RepoMetaDataSerializer.CATEGORY)
