import os
import shutil

from dotenv import load_dotenv
from loguru import logger

from src.adapters.RepoModelListAdapter import RepoModelListAdapter
from src.categories.AwesomeCategory import AwesomeCategory
from src.categories.TopicCategory import TopicCategory
from src.helpers.FileManager import FileManager
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer


awesome_list_name = "Hannibal046/Awesome-LLM"
# load .env



logger.info("Generating awesome lists")
load_dotenv()

access_token  = os.getenv("CREDENTIALS")   
has_replace = os.getenv("REPLACE","False")
has_replace = has_replace.lower() == "true"


import os
import shutil
import logging

logger = logging.getLogger(__name__)

def get_awesome_lists_iterator(file_path):
    with open(file_path, "r") as lists_file:
        for line in lists_file:
            awesome_list_name = line.strip()
            awesome_list_name = awesome_list_name.replace("https://github.com/", "")
            yield awesome_list_name

def get_topics_iterator(directory, max_files=None):
    filenames = os.listdir(directory)
    filenames = filenames[:max_files] if max_files else filenames
    
    for filename in filenames:
        if filename.endswith(".json"):
            yield filename[:-5]  # Remove the .json extension
        else:
            continue
        
def create_awesome_category(access_token, has_replace):
    if has_replace:
        # Delete all the files in the directory ./var/repo
        shutil.rmtree("./var/repo", ignore_errors=True)
        logger.info("Deleted all the files in the directory ./var/repo")

    # Ensure that the directory ./var/repo exists
    if not os.path.exists("./var/repo"):
        os.makedirs("./var/repo")
        logger.info("Created the directory ./var/repo")

    # Load lists.txt file and for each line create a category
    for awesome_list_name in get_awesome_lists_iterator("lists.txt"):
        try:
            logger.info(f"Loading awesome list {awesome_list_name}")
            awesome_category = AwesomeCategory(awesome_list_name, access_token)
            del(awesome_category)
        except Exception as e:
            logger.exception(f"An error occurred while loading the awesome list {e}")
            pass

def create_topic_category(access_token, has_replace):
    if has_replace:
        # Delete all the files in the directory ./var/topic
        shutil.rmtree("./var/topic", ignore_errors=True)
        logger.info("Deleted all the files in the directory ./var/topic")

    if not os.path.exists("./var/topic"):
        os.makedirs("./var/topic")
        logger.info("Created the directory ./var/topic")

    # Load all the repos from the directory ./var/repo
    repo_list = []
    # Load the first MAX_REPOS_DEBUG repos, for debugging purposes
    MAX_REPOS_DEBUG = 50000
    repo_list = [RepoMetaDataSerializer.from_file(filename) for filename in get_topics_iterator("./var/repo", MAX_REPOS_DEBUG)]
    logger.info(f"Loaded {len(repo_list)} repos from the directory ./var/repo")
    repo_list = RepoModelListAdapter.adapt(repo_list)
    logger.info(f"Adapted {len(repo_list)} repos from the directory ./var/repo")

    # Extract all the topics from the repos, and create a set with all the topics
    topics_array = []
    for repo in repo_list:
        topics_array.extend(repo.topics)
    
    # Sort by start and delete duplicates for topics_array
    # (Assuming you have more code here to handle topics_array)        
    topics_set = sorted(set(topics_array))
    for topic in topics_set:
        try:
            logger.info(f"Loading topic {topic}")
            topic_category = TopicCategory(topic, repo_list)
            del(topic_category) # Serialize the data when the object is deleted
        except Exception as e:
            logger.exception(f"An error occurred while loading the topic {e}")
            pass
        
    logger.info(f"Loaded {len(topics_set)} topics from the directory ./var/repo")



if __name__ == "__main__":
    has_replace= False
    create_awesome_category(access_token, has_replace)
    create_topic_category(access_token, has_replace)
    
    backend_dir = "~/git/managing-awesome-lists"
    frontend_dir = "~/git/managing-awesome-lists-frontend"  
    file_manager = FileManager(backend_dir, frontend_dir)
    file_manager.run()


    