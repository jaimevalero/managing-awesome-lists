from typing import List
from src.helpers.RepoModelList import delete_duplicates
from src.models.RepoModel import RepoModel

class RepoModelListAdapter:
    """
    A helper class that provides static methods to manipulate lists of RepoModel objects.

    This class provides methods to delete duplicate RepoModel objects (the same repo served
    under two names after being transferred to another owner),
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
        # Deduplication lives in the helper, so lists and topics drop the same duplicates
        return delete_duplicates(repo_list)

    @staticmethod
    def sort_by_star(repo_list: List[RepoModel]):
        return sorted(repo_list, key=lambda x: x.stargazers_count, reverse=True)

    @staticmethod
    def adapt(repo_list: List[RepoModel]):
        return RepoModelListAdapter.sort_by_star(RepoModelListAdapter.delete_duplicates(repo_list))