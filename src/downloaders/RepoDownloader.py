from loguru import logger
import requests
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer 

from src.adapters.RepoAdapter import RepoAdapter
from itertools import product
from http import HTTPStatus
import requests
from typing import List
from src.models.RepoModel import  RepoModel
class ReadmeDownloader:
    """
    A utility class for downloading README files from GitHub repositories.

    This class provides a static method `download_readme` that attempts to download
    the README file from a given GitHub repository. It tries different combinations
    of branch names and README file names until it finds an existing file.

    Attributes:
        None

    Methods:
        download_readme(repo_meta_data_name: str, access_token: str) -> str:
            Attempts to download the README file from the GitHub repository specified
            by `repo_meta_data_name`. Uses the provided `access_token` for authentication.
            Returns the content of the README file as a string, or `None` if no README file
            could be found.
    """    
    @staticmethod
    def download_readme(repo_meta_data_name, access_token):
        branches = ["master", "main"]
        readme_combinations = [ 
            "README.md", 
            "readme.md",
            "Readme.md", 
            "readme.MD", 
            "README.MD",
            "Readme.MD", 
        ]
        readme_content = None
        for branch, readme_combination in product(branches, readme_combinations):
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f"https://raw.githubusercontent.com/{repo_meta_data_name}/{branch}/{readme_combination}")
            if response.status_code == HTTPStatus.OK:
                readme_content = response.text
                break
        return readme_content
    
class RepoListDownloader:
    """
    Class for downloading a list of GitHub repositories.

    When instantiating this class, a query is made to the GitHub API to fetch data for the specified repositories and a list of RepoModel instances is returned.

    Attributes:
        access_token (str): Access token for the GitHub API.
        repo_full_names (list): List of full names of the repositories to download.
        repos_data (list): List of RepoModel instances for the downloaded repositories.

    Methods:
        fetch_repository_data(): Makes the query to the GitHub API and stores the repository data in repos_data.
        __get_repository_data_cache(repo_full_names): Checks the cache for repository data before making the API query.
    """
    def __new__(cls, access_token, repo_full_names) -> List[RepoModel]:
        """
        Overridden method that is called before __init__ when an instance is created.

        This method fetches data for the specified repositories from the GitHub API and returns a list of RepoModel instances.

        Args:
            access_token (str): Access token for the GitHub API.
            repo_full_names (list): List of full names of the repositories to download.

        Returns:
            list: A list of RepoModel instances representing the downloaded repositories.
        """        
        instance = super(RepoListDownloader, cls).__new__(cls)
        instance.access_token = access_token
        instance.repo_full_names = repo_full_names
        instance.repos_data = instance.fetch_repository_data()
 
        return instance.repos_data
    
    def fetch_repository_data(self):
        access_token = self.access_token
        repo_full_names = self.repo_full_names
        repos_data = []
        # GitHub GraphQL API endpoint
        api_url = 'https://api.github.com/graphql'

        # GraphQL query for multiple repositories
        graphql_query = '''
        query {
          %s
        }
        '''
        # Look for data in the cache, before making the request to graph ql
        repos_data, repo_full_names = self.__get_repository_data_cache(repo_full_names)
        logger.debug(f"Cached repos: {len(repos_data)}. Not cached respo:  {len(repo_full_names)}")
                     
        if repos_data:
            repos_data.extend(repos_data)

            
        # Prepare the list of repositories for the query
        REPO_GROUP_SIZE = 20
        for i in range(0, len(repo_full_names), REPO_GROUP_SIZE):

            repo_block = repo_full_names[i:i+REPO_GROUP_SIZE]
                      
            repositories_query = ''
            for index, repo in enumerate(repo_block):
                short_repo = repo.split('/', 2)[:2]
                short_repo = '/'.join(short_repo)
                if not "/" in short_repo:
                    logger.warning(f"Bad format for repo: "+ str(short_repo)) 
                    continue # bad repo name

                owner, name = short_repo.split('/')
                repo_query = f'repo_{index}: repository(owner: "{owner}", name: "{name}") {{\n' \
                            f'  nameWithOwner\n  description\n  repositoryTopics(first: 10) {{ nodes {{ topic {{ name }} }} }}\n  createdAt\n' \
                            f'  pushedAt\n  stargazers {{ totalCount }}\n  languages(first: 1) {{ edges {{ node {{ name }} }} }}\n}}'              
                repositories_query += repo_query + '\n'

            # Construct the final GraphQL query
            final_query = graphql_query % repositories_query

            # Prepare the request payload
            headers = {'Authorization': f'Bearer {access_token}'}
            payload = {'query': final_query}

            # Make the request to GitHub API, to load block of metadata for multiple repositories   
            response = requests.post(api_url, headers=headers, json=payload)
            for repo_data in response.json()['data'].values():
                # Crate a topic plane list 
                if not repo_data:
                    logger.warning(f"Error downloading repo "+ str(response.json()["errors"]))
                else : 
                    repo_data = RepoAdapter.convert_graphql_to_repo_metadata(repo_data)
                    repos_data.append(repo_data)
        self.repos_data  = repos_data
        return repos_data

    def __get_repository_data_cache(self, repo_full_names):
        cached_repos = []
        repo_full_names_curated =  repo_full_names.copy()
        for repo_full_name in repo_full_names:
            # If file containing the data already exists, load it
            #logger.info(f"Size of repo_full_names_curated: {len(repo_full_names_curated)}, {len(repos_data)}")
            if RepoMetaDataSerializer.exists_file(repo_full_name):
                try :
                    repo_load_from_file = RepoMetaDataSerializer.from_file(repo_full_name) 
                    cached_repos.append(repo_load_from_file)
                    # remove the repo from the list
                    if repo_load_from_file:
                        repo_full_names_curated.remove(repo_full_name)
                except:
                    logger.warning(f"Error loading repo "+ str(repo_full_name))
            else:
                logger.warning(f"Repo not found in cache "+ str(repo_full_name))
                
        return cached_repos, repo_full_names_curated
    