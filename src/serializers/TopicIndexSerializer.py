
import json
import os
from typing import List

from loguru import logger

from src.models.TopicIndexModel import TopicIndexModel
from src.serializers.AbstractSerializer import AbstractSerializer


class TopicIndexSerializer(AbstractSerializer):
    """
    A subclass of AbstractSerializer that builds and serializes the topic search index.

    TopicSerializer writes one .json file per topic in "./var/topic". Those files are
    what the frontend renders, but they are far too many to search through in the
    browser. This class reads that directory and writes a single index file
    (name + number of repos per topic) that the frontend search bar can load in one
    request to offer topics as search results.

    Attributes
    ----------
    CATEGORY : str
        The category of the repositories. In this case, it's "topic".
    MIN_REPOS : int
        Topics with fewer repos than this are left out of the index. The median topic
        has a single repo, so indexing them all is mostly noise for whoever searches.
    INDEX_FILENAME : str
        Default name of the generated index file.

    Methods
    -------
    from_directory(topics_dir: str) -> List[TopicIndexModel]
        Reads the serialized topics and returns the index entries, sorted by number of
        repos (descending), so the frontend can just take the first results.
    to_file(topics: List[TopicIndexModel], object_serialized_path: str)
        Serializes the given index entries to a .json file.
    """

    CATEGORY = "topic"
    MIN_REPOS = 2
    INDEX_FILENAME = "topics.json"

    @staticmethod
    def from_directory(topics_dir: str = None) -> List[TopicIndexModel]:
        topics_dir = topics_dir or f"./var/{TopicIndexSerializer.CATEGORY}"
        topics = []

        for filename in os.listdir(topics_dir):
            if not filename.endswith(".json"):
                continue
            try:
                # Only the repo count is needed, so the file is read raw instead of
                # rebuilding a full TopicModel for each of the ~26.000 topics.
                with open(f"{topics_dir}/{filename}") as f:
                    repos = len(json.load(f).get("repos_data") or [])
            except Exception as e:
                logger.exception(f"Error reading topic file {filename} {e}")
                continue

            if repos >= TopicIndexSerializer.MIN_REPOS:
                topics.append(TopicIndexModel(name=filename[: -len(".json")], repos=repos))

        return sorted(topics, key=lambda topic: (-topic.repos, topic.name))

    @staticmethod
    def to_file(topics: List[TopicIndexModel], object_serialized_path: str = None):
        object_serialized_path = object_serialized_path or f"./{TopicIndexSerializer.INDEX_FILENAME}"
        with open(object_serialized_path, 'w') as f:
            f.write(json.dumps([topic.model_dump() for topic in topics]))
        logger.info(f"Wrote {len(topics)} topics to {object_serialized_path}")
