

from src.downloaders.RepoDownloader import ReadmeDownloader, RepoListDownloader
from src.populators.AbstractPopulator import AbstractPopulator
from loguru import logger
import os
import re
from dotenv import load_dotenv
from typing import List
from src.models.RepoModel import RepoModel  
class AwesomePopulator(AbstractPopulator):
    """ This class represents an interface for populating, 
        given a name of an awesome list in github, 
        return list of its repos"""

    def populate(self) -> List[RepoModel]:
        repo_names = self.__get_repo_names_from_readme()
        access_token = self.access_token
        repos_data = RepoListDownloader(access_token,repo_names)
        self.repos_data = repos_data
        return repos_data
    
    def __get_repo_names_from_readme(self):
        repo_meta_data_name = self.name
        access_token = self.access_token

        # Assert that the access token is not none nor empty
        assert access_token != None, "Access token is none"
        assert access_token != "", "Access token is empty"


        logger.info(f"Populating repo list for awesome {repo_meta_data_name}")

        repo_names = []
        try : 
            readme_text = ReadmeDownloader.download_readme(repo_meta_data_name, access_token)
            regexp = r"\[.*\]\(https:\/\/github\.com\/(.*)\)"
            matches = re.findall(regexp, readme_text)
            matches = [match.split("#")[0] for match in matches]
            matches = [match.split("(")[0] for match in matches]
            matches = [match.split(")")[0] for match in matches]
            # Remove those that not contains / character
            matches = [match for match in matches if "/" in match]
            matches=  [match.split("/")[0]+"/"+match.split("/")[1] for match in matches]


            repo_names = matches
        except Exception as e:
            logger.exception(f"Error with {repo_meta_data_name} {e}")
        finally:
            return repo_names
        

def main():
    # Load the .env file
    load_dotenv()
    access_token = os.getenv("CREDENTIALS")
    awesome_list_name = "sindresorhus/awesome"

    with AwesomePopulator(access_token, awesome_list_name) as populator:
        for repo in populator:
            print(repo)  # Haz algo con cada repositorio

if __name__ == "__main__":
    main()


    
# main, for testing purposes

    