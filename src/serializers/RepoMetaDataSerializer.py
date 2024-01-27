      

from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel  
from src.serializers.AbstractSerializer import AbstractSerializer
import json

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
