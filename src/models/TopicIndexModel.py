from pydantic import BaseModel


class TopicIndexModel(BaseModel):
    """ This class is for serializing one entry of the topic search index.

    The frontend search bar needs to look up topics by name, but the topic pages
    are ~26.000 separate json files. This model is the light row (name + how many
    repos the topic has) that goes into the single index file the frontend loads.
    """
    name: str
    repos: int
