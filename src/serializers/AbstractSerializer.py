from src.models.RepoModel import RepoModel
import os
class AbstractSerializer:
    """
    An abstract base class that provides a structure for serializing and deserializing RepoModel objects.

    This class provides methods to check if a serialized file exists for a given repository name and category,
    serialize a RepoModel object to a file, and deserialize a RepoModel object from a file.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. This should be overridden by subclasses.

    Methods
    -------
    exists_file(repo_name: str, category: str) -> bool
        Checks if a serialized file exists for the given repository name and category.
        Returns True if the file exists, False otherwise.

    to_file(object: RepoModel)
        Serializes the given RepoModel object to a file. This method should be implemented by subclasses.

    from_file(name: str) -> RepoModel
        Deserializes a RepoModel object from a file with the given name. This method should be implemented by subclasses.
    """
    ...    
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