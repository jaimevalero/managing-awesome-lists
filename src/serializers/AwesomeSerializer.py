
from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel  
from src.serializers.AbstractSerializer import AbstractSerializer

class AwesomeSerializer(AbstractSerializer):
    CATEGORY = "awesome"
    @staticmethod
    def to_file(awesome_category):
        
        repo_meta_data = awesome_category.repo_meta_data
        awesome_model = AwesomeModel(
            category_type=awesome_category.category_type,
            category_name=awesome_category.category_name,
            repo_meta_data=awesome_category.repo_meta_data,
            repo_list_models=awesome_category.repo_list_models,
            frecuent_topics=awesome_category.frecuent_topics
        )        
        filename_clean = repo_meta_data.full_name.replace('/', '@')

        
        object_serialized_path = f"./var/{AwesomeSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
                    f.write(awesome_model.model_dump_json())
  