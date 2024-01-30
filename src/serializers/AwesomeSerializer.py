
import json
from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel  
from src.serializers.AbstractSerializer import AbstractSerializer

class AwesomeSerializer(AbstractSerializer):
    """
    A subclass of AbstractSerializer that provides serialization and deserialization for AwesomeModel objects.

    This class overrides the to_file method of AbstractSerializer to provide a way to serialize AwesomeModel objects.
    The serialized objects are stored in a .json file in the "./var/awesome" directory. The filename is based on the 
    full_name attribute of the repo_meta_data of the AwesomeModel, with '/' replaced by '@'.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. In this case, it's "awesome".

    Methods
    -------
    to_file(awesome_category: AwesomeModel)
        Serializes the given AwesomeModel object to a .json file. The filename is based on the full_name attribute of 
        the repo_meta_data of the AwesomeModel, with '/' replaced by '@'.
    """
    ...
    CATEGORY = "awesome"
    @staticmethod
    def to_file(awesome_category):
        
        repo_meta_data = awesome_category.repo_meta_data
        awesome_model = AwesomeModel(
            category_type=awesome_category.category_type,
            category_name=awesome_category.category_name,
            repo_meta_data=awesome_category.repo_meta_data,
            repos_data=awesome_category.repos_data,
            frecuent_topics=awesome_category.frecuent_topics
        )        
        filename_clean = repo_meta_data.full_name.replace('/', '@')

        
        object_serialized_path = f"./var/{AwesomeSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
                    f.write(awesome_model.model_dump_json())
 
    @staticmethod
    def from_file(filename: str) -> AwesomeModel:
        with open(filename) as f:
            data = json.load(f)
        return AwesomeModel(**data)    