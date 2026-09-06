      

from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel  
from src.serializers.AbstractSerializer import AbstractSerializer
from datetime import datetime, timedelta, timezone
import json
import os

class RepoMetaDataSerializer(AbstractSerializer):
    """
    Class for serializing and deserializing instances of RepoMetaData to and from a file.

    Methods:
        to_file(repo_meta_data: RepoMetaData, filename: str): Saves an instance of RepoMetaData to a file.
        from_file(filename: str) -> RepoMetaData: Loads an instance of RepoMetaData from a file.
    """
    CATEGORY = "repo"
    # Days a cached repo is considered usable. pushed_at and stargazers_count are the
    # whole point of this cache and both go stale, so without an expiry the first
    # download of a repo is the one shown forever. 0 disables the expiry.
    DEFAULT_CACHE_TTL_DAYS = 7


    @staticmethod
    def to_file(repo_meta_data: RepoModel):
        filename_clean = repo_meta_data.full_name.replace('/', '@')
        # Overwrite the file if it already exists
        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename_clean}.json", 'w') as f:
                    f.write(repo_meta_data.model_dump_json())


    @staticmethod
    def from_file(repo_name: str) -> RepoModel:
        filename = repo_name.replace('/', '@')

        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename}.json") as f:
            data = json.load(f)
        return RepoModel(**data)
    
    @staticmethod
    def cache_ttl_days() -> float:
        """ Read at call time and not at import time, so tests and one-off runs can move
        it with CACHE_TTL_DAYS without reloading the module """
        try:
            return float(os.getenv("CACHE_TTL_DAYS", RepoMetaDataSerializer.DEFAULT_CACHE_TTL_DAYS))
        except ValueError:
            return float(RepoMetaDataSerializer.DEFAULT_CACHE_TTL_DAYS)

    @staticmethod
    def exists_file(repo_name:str) -> bool:
        """ True when the repo is cached *and* the cached copy is still fresh.

        The freshness comes from cached_at inside the file and not from its mtime,
        because every run rewrites the file of every repo of every list it touches,
        cached ones included, so the mtime says when the file was last written and not
        when its contents were downloaded.

        Returning False for an expired copy is enough to renew it: the downloader asks
        github for whatever is not in the cache and overwrites the file with the answer.
        """
        # We invoke the static method from the parent class
        if not AbstractSerializer.exists_file(repo_name,RepoMetaDataSerializer.CATEGORY):
            return False

        ttl_days = RepoMetaDataSerializer.cache_ttl_days()
        if ttl_days <= 0:
            return True

        try:
            cached_at = RepoMetaDataSerializer.from_file(repo_name).cached_at
        except Exception:
            # Unreadable or from an older shape of the model: treat it as not cached
            return False

        if cached_at is None:
            # Cached before the download date started being recorded
            return False
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - cached_at < timedelta(days=ttl_days)
