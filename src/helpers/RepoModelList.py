
from typing import List
from src.models.RepoModel import RepoModel
from loguru import logger

def delete_duplicates(repo_list: List[RepoModel])-> List[RepoModel]:
    """ This function deletes duplicates from a list of repos
    """
    # Key is full_name
    try :
        seen = set()
        new_list = []
        for repo in repo_list:
            lower_name = repo.full_name.lower()
            if lower_name not in seen:
                seen.add(lower_name)
                new_list.append(repo)
        return new_list
    except Exception as e:
        logger.error(e)
        return repo_list
    
def sort_by_star(repo_list: List[RepoModel])-> List[RepoModel]:
    """ This function sorts a list of repos by stars, descending
    """
    try : 
        return sorted(repo_list, key=lambda x: x.stargazers_count, reverse=True)
    except Exception as e:
        logger.exception(e)
        return repo_list

def get_frecuent_topics(repo_list: List[RepoModel],max_elements=5)-> dict:
    """ This function count the frequency of each topic for all RepoModel. 
    Return a list with those frequencies are higer
    """
    try:
        # Create a dictionary with the frequency of each topic
        topics_dict = {}
        for repo in repo_list:
            for topic in repo.topics:
                if topic in topics_dict:
                    topics_dict[topic] += 1
                else:
                    topics_dict[topic] = 1
        # Sort the dictionary by value, descending
        topics_dict = dict(sorted(topics_dict.items(), key=lambda item: item[1], reverse=True))
        # Get the first max_elements elements
        topics_dict = dict(list(topics_dict.items())[:max_elements])
        return topics_dict
    except Exception as e:
        logger.exception(e)
        return {}