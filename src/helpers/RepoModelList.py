
from typing import List
from src.models.RepoModel import RepoModel
from loguru import logger

def delete_duplicates(repo_list: List[RepoModel])-> List[RepoModel]:
    """ This function deletes duplicates from a list of repos

    A repo is a duplicate of another when both are the same repo under two different
    names, which happens when the repo is transferred to another owner and github keeps
    serving it under both (see RepoModel.is_same_repo_as). The copy that survives is the
    one at the name the repo lives at now; when nothing recorded which name that is, the
    least outdated copy is kept instead.
    """
    try :
        # Repos are grouped by identity (the creation date) so that each repo is only
        # compared against the handful of repos created in that same second.
        kept_by_identity = {}
        for repo in repo_list:
            duplicates = kept_by_identity.setdefault(repo.identity, [])
            for index, kept in enumerate(duplicates):
                if repo.is_same_repo_as(kept):
                    if repo.is_current_name_of(kept) or (
                        not kept.is_current_name_of(repo) and repo.is_fresher_than(kept)
                    ):
                        logger.debug(f"Repo {kept.full_name} is an old name of {repo.full_name}, keeping the latter")
                        duplicates[index] = repo
                    else:
                        logger.debug(f"Repo {repo.full_name} is an old name of {kept.full_name}, keeping the latter")
                    break
            else:
                duplicates.append(repo)

        # The repos keep the order they came in, deduplication should not reorder them
        kept = {id(repo) for duplicates in kept_by_identity.values() for repo in duplicates}
        deduplicated = [repo for repo in repo_list if id(repo) in kept]
        # One line instead of one per duplicate: a monthly batch that prints 300 lines
        # about repos that changed owner is a batch nobody reads
        if len(deduplicated) < len(repo_list):
            logger.info(f"Deleted {len(repo_list) - len(deduplicated)} repos duplicated under an old name")
        return deduplicated
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