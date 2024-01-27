from typing import List
from src.models.RepoModel import RepoModel

class RepoModelListAdapter:
    """
    A helper class that provides static methods to manipulate lists of RepoModel objects.

    This class provides methods to delete duplicate RepoModel objects based on their full_name attribute,
    sort RepoModel objects by their stargazers_count attribute, and adapt a list of RepoModel objects
    by deleting duplicates and sorting by stargazers_count.

    Methods
    -------
    delete_duplicates(repo_list: List[RepoModel])
        Returns a new list from the input list with duplicate RepoModel objects removed.

    sort_by_star(repo_list: List[RepoModel])
        Returns a new list from the input list with RepoModel objects sorted by stargazers_count in descending order.

    adapt(repo_list: List[RepoModel])
        Returns a new list from the input list with duplicate RepoModel objects removed and remaining objects sorted by stargazers_count in descending order.
    """    
    @staticmethod
    def delete_duplicates(repo_list: List[RepoModel]):
        seen = set()
        new_list = []
        for repo in repo_list:
            if repo.full_name not in seen:
                seen.add(repo.full_name)
                new_list.append(repo)
        return new_list

    @staticmethod
    def sort_by_star(repo_list: List[RepoModel]):
        return sorted(repo_list, key=lambda x: x.stargazers_count, reverse=True)

    @staticmethod
    def adapt(repo_list: List[RepoModel]):
        return RepoModelListAdapter.sort_by_star(RepoModelListAdapter.delete_duplicates(repo_list))