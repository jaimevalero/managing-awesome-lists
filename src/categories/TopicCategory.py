from typing import List
from src.serializers.TopicSerializer import TopicSerializer
from src.categories.AbstractCategory import AbstractCategory

from src.populators.TopicPopulator import TopicPopulator
from src.models.RepoModel import RepoModel  
from loguru import logger

class TopicCategory(AbstractCategory):
    """ This class represents a given topic in github, containing a list of repos"""
    def __init__(self, category_name : str, all_repos: List[RepoModel],category_type="topic"):
        #super().__init__(category_name, "", TopicPopulator(repos_data, category_name), TopicSerializer,category_type=category_type)
        self.all_repos = all_repos
        super().__init__(category_name, "", TopicPopulator(all_repos,category_name), TopicSerializer,category_type=category_type)
        logger.info(f"Populating topic {category_name} with {len(self.repos_data)} repos")



    

        
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


            

