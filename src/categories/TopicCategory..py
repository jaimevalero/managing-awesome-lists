
import re
from typing import List
from src.downloaders.RepoDownloader import ReadmeDownloader

from populators.AwesomePopulator import AwesomeListPopulator
from src.serializers.RepoSerializer import AbstractSerializer, AwesomeSerializer
from src.populators.AbstractPopulator import AbstractPopulator
from models.RepoModel import RepoModel  
from abc import ABC
from loguru import logger

class TopicCategory(AbstractCategory):
    """ This class represents a given topic in github, containing a list of repos"""
    def __init__(self, RepoMetaData: RepoModel):
        self.category_name = "topic"
        self.RepoMetaData = RepoMetaData
        self.RepoList = []
        self.populate_repo_list()

    def populate_repo_list(self):
        for topic in self.RepoMetaData.topics:
            self.RepoList.append(topic)
