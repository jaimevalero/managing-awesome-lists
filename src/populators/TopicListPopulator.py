

class TopicListPopulator(object):
    def __init__(self, topic_list):
        self.topic_list = topic_list

    def populate(self, topic_list):
        for topic in topic_list:
            self.topic_list.add_topic(topic