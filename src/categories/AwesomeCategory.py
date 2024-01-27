from src.categories.AbstractCategory import AbstractCategory
from src.populators.AwesomePopulator import AwesomePopulator
from src.serializers.AwesomeSerializer import AwesomeSerializer
from loguru import logger
import os
import re
from dotenv import load_dotenv
from src.downloaders.RepoDownloader import RepoListDownloader


class AwesomeCategory(AbstractCategory):
    """ This class represents an awesome list in github, containing a list of repos"""
    def __init__(self, category_name : str, access_token = ""):
        super().__init__(category_name, access_token, AwesomePopulator, AwesomeSerializer)
        self.category_type = "awesome"
        self.repo_meta_data = RepoListDownloader(access_token,[category_name])[0]



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


            