from src.helpers.RepoModelList import delete_duplicates, sort_by_star
from src.adapters.RepoModelListAdapter import RepoModelListAdapter
from src.categories.AwesomeCategory import AwesomeCategory
from src.categories.TopicCategory import TopicCategory
from src.populators.AwesomePopulator import AwesomePopulator
from src.serializers.RepoMetaDataSerializer import RepoMetaDataSerializer
from loguru import logger
from dotenv import load_dotenv
import os

awesome_list_name = "Hannibal046/Awesome-LLM"
# load .env



logger.info("Generating awesome lists")
load_dotenv()

access_token  = os.getenv("CREDENTIALS")   
has_replace = os.getenv("REPLACE","False")
has_replace = has_replace.lower() == "true"


def create_awesome_category(access_token, has_replace):

    if has_replace:
    # Delete all the files in the directory ./var/repo, 
        import shutil
        shutil.rmtree("./var/repo", ignore_errors=True)
        logger.info("Deleted all the files in the directory ./var/repo")

# Ensure that the directory ./var/repo exists
    if not os.path.exists("./var/repo"):
        os.makedirs("./var/repo")
        logger.info("Created the directory ./var/repo")

# Load lists.txt file and for each line create a category
    with open("lists.txt", "r") as lists_file:
        for line in lists_file:
            try:
                awesome_list_name = line.strip()
            # remove "https://github.com/" from the name
                awesome_list_name = awesome_list_name.replace("https://github.com/","")
                logger.info(f"Loading awesome list {awesome_list_name}")
                awesome_category = AwesomeCategory(awesome_list_name, access_token)
                del(awesome_category)
            except Exception as e:
                logger.exception(f"An error occurred while loading the awesome list {e}")
                pass

def create_topic_category(access_token, has_replace):

    if has_replace:
    # Delete all the files in the directory ./var/repo, 
        import shutil
        shutil.rmtree("./var/topic", ignore_errors=True)
        logger.info("Deleted all the files in the directory ./var/topic")

    if not os.path.exists("./var/topic"):
        os.makedirs("./var/topic")
        logger.info("Created the directory ./var/topic")

    # Load all the repos from the directory ./var/repo
    repo_list = []
    # Carga los primeros MAX_REPOS_DEBUG repos, for debugging purposes
    MAX_REPOS_DEBUG= 20000
    for filename in os.listdir("./var/repo")[:MAX_REPOS_DEBUG]:
        if filename.endswith(".json"):
            # Remove the .json extension, but only the last one
            filename = filename[:-5]
            # Load the repo from the file
            repo_list.append(RepoMetaDataSerializer.from_file(filename))
        else:
            continue
    logger.info(f"Loaded {len(repo_list)} repos from the directory ./var/repo")
    repo_list = RepoModelListAdapter.adapt(repo_list)
    logger.info(f"Adapted {len(repo_list)} repos from the directory ./var/repo")
    # Extrac all the topics from the repos, and create a set with all the topics
    topics_array = []
    for repo in repo_list:
        topics_array.extend(repo.topics)
    # Sort by start and delete duplicates for topics_array


         
    topics_set = sorted(set(topics_array))
    for topic in topics_set:
        try:
            logger.info(f"Loading topic {topic}")
            topic_category = TopicCategory(topic, repo_list)
            del(topic_category)
        except Exception as e:
            logger.exception(f"An error occurred while loading the topic {e}")
            pass
        
    logger.info(f"Loaded {len(topics_set)} topics from the directory ./var/repo")

    

if __name__ == "__main__":
    #create_awesome_category(access_token, has_replace)
    create_topic_category(access_token, has_replace)


    