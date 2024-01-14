
from typing import List
from src.models.RepoModel import RepoModel

def delete_duplicates(repo_list: List[RepoModel]):
    """ This function deletes duplicates from a list of repos
    """
    # Key is full_name
    seen = set()
    new_list = []
    for repo in repo_list:
        lower_name = repo.full_name.lower()
        if lower_name not in seen:
            seen.add(lower_name)
            new_list.append(repo)
    return new_list

def sort_by_star(repo_list: List[RepoModel]):
    """ This function sorts a list of repos by stars, descending
    """
    return sorted(repo_list, key=lambda x: x.stargazers_count, reverse=True)
