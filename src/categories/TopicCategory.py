from typing import List
from src.serializers.TopicSerializer import TopicSerializer
from src.categories.AbstractCategory import AbstractCategory

from src.populators.TopicPopulator import TopicPopulator
from src.models.RepoModel import RepoModel  
from loguru import logger

class TopicCategory(AbstractCategory):
    """ This class represents a given topic in github, containing a list of repos"""
    def __init__(self, category_name : str, all_repo_models : List[RepoModel]):
        self.category_type = "topic"
        self.category_name = category_name
        self.populator = TopicPopulator(all_repo_models, category_name)
        self.serializer = TopicSerializer       
        self.repo_list_models = self.populator.populate()        
        logger.info(f"Populating topic {category_name} with {len(self.repo_list_models)} repos")
        self.frecuent_topics = self.get_frecuent_topics(self.repo_list_models)
    def to_file(self):
        self.serializer.to_file(self)
        pass 
    
    def __del__(self):
        """ Serialize the data from the repos when the object is deleted """
        self.to_file()
        
# def main():
#     # Load the .env file
#     load_dotenv()
#     access_token = os.getenv("CREDENTIALS")
#     awesome_list_name = "viatsko/awesome-vscode"

#     awesome_category = AwesomeCategory(awesome_list_name, access_token)
#     #awesome_category.to_file()
#     a = 0
# if __name__ == "__main__":
#     main()


            

