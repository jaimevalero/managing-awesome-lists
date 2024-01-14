from typing import List
from src.models.RepoModel import RepoModel

class RepoModelListAdapter:
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