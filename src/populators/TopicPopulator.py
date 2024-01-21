from src.populators.AbstractPopulator import AbstractPopulator
from loguru import logger

class TopicPopulator(AbstractPopulator):
    """ This class extract the repos from a list of repos 
    that have a given topic"""
    def __init__(self, repos_data, category_name):
        self.repos_data = repos_data
        self.category_name = category_name
        self.topic_list = []
    def populate(self):
        repos_data = self.repos_data
        category_name = self.category_name
        topic_list = self.topic_list
        # Iterate trough all the repos, and chose the ones that have the topic, category_name in the topics list
        for repo_model in repos_data:
            if category_name in repo_model.topics:
                topic_list.append(repo_model)
        logger.info(f"Populating topic {category_name} with {len(self.topic_list)} repos")
        # Avoid duplicates, and sort by stars
        topic_list = self.normalize(topic_list)
        self.topic_list = topic_list
        return topic_list
    