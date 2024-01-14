from src.categories.AbstractCategory import AbstractCategory
from src.populators.AwesomePopulator import AwesomePopulator
from src.serializers.AwesomeSerializer import AwesomeSerializer
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer
from loguru import logger
import os
import re
from dotenv import load_dotenv
from src.downloaders.RepoDownloader import RepoListDownloader


class AwesomeCategory(AbstractCategory):
    """ This class represents an awesome list in github, containing a list of repos"""
    def __init__(self, category_name : str, access_token = ""):
        self.category_type = "awesome"
        self.access_token = access_token
        self.category_name = category_name
        self.repo_meta_data = None
        self.populator = AwesomePopulator
        self.serializer = AwesomeSerializer
        self.repo_meta_data = RepoListDownloader(access_token,[category_name])[0]
        self.repo_list_models = self.populator(self.access_token, self.category_name).populate()
        self.frecuent_topics = self.get_frecuent_topics(self.repo_list_models)
    def to_file(self):
        self.serializer.to_file(self)

    def serialize_repo_data(self):
        """ Serialize the repo data to a file """
        for repo_model in self.repo_list_models:
            RepoMetaDataSerializer.to_file(repo_model)   

    def __del__(self):
        """ Serialize the data from the repos when the object is deleted """
        self.serialize_repo_data()
        self.to_file()
# Main
def main():
    # Load the .env file
    load_dotenv()
    access_token = os.getenv("CREDENTIALS")
    awesome_list_name = "viatsko/awesome-vscode"

    awesome_category = AwesomeCategory(awesome_list_name, access_token)
    #awesome_category.to_file()
    a = 0
if __name__ == "__main__":
    main()


            