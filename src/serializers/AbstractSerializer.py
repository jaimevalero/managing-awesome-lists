from src.models.RepoModel import RepoModel
import os

class AbstractSerializer:
    CATEGORY = None

    @staticmethod
    def exists_file(repo_name:str,category) -> bool:
        filename = repo_name.replace('/', '@')
        return os.path.isfile(f"./var/{category}/{filename}.json")


    @staticmethod
    def to_file(object):
        pass

    @staticmethod
    def from_file(name: str) -> RepoModel:
        pass