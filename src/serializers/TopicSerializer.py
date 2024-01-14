
from src.categories.AbstractCategory import AbstractCategory
from src.models.TopicModel import TopicModel        
from src.serializers.AbstractSerializer import AbstractSerializer





class TopicSerializer(AbstractSerializer):
    """
    A subclass of AbstractSerializer that provides serialization for TopicModel objects.

    This class overrides the to_file method of AbstractSerializer to provide a way to serialize TopicModel objects.
    The serialized objects are stored in a .json file in the "./var/topic" directory. The filename is based on the 
    category_name attribute of the TopicModel, with '/' replaced by '@'.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. In this case, it's "topic".

    Methods
    -------
    to_file(topic_category: AbstractCategory)
        Serializes the given TopicModel object to a .json file. The filename is based on the category_name attribute of 
        the TopicModel, with '/' replaced by '@'.
    """
    
    CATEGORY = "topic"
    @staticmethod
    def to_file(topic_category:AbstractCategory):
        
        topic_model = TopicModel(
            category_type=topic_category.category_type,
            category_name=topic_category.category_name,
            repo_list_models=topic_category.repo_list_models,
            frecuent_topics=topic_category.frecuent_topics
        )        
        filename_clean = topic_model.category_name.replace('/', '@')
        object_serialized_path = f"./var/{TopicSerializer.CATEGORY}/{filename_clean}.json"
        with open(object_serialized_path, 'w') as f:
                    f.write(topic_model.model_dump_json())

