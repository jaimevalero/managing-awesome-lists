from dateutil.parser import parse
from pydantic import BaseModel, conint, conlist, constr, field_validator


from typing import Optional
from datetime import datetime

class RepoModel(BaseModel):
    """
    Model for storing metadata of a repository.

    Attributes:
        full_name (str): Full name of the repository.
        description (str): Description of the repository.
        topics (list[str]): List of topics of the repository.
        created_at (datetime): Creation date of the repository.
        pushed_at (datetime): Date of the last update of the repository.
        stargazers_count (int): Number of stars of the repository.
        language (str): Main language of the repository.
        transferred_to (str): Current full name of the repository, when full_name is the
            old one it was transferred from. None while full_name is the current one.
    """
    full_name: str
    description: str
    topics: conlist(str)
    created_at: datetime
    pushed_at: datetime
    stargazers_count: conint(ge=0)
    # language is an array of strings or None
    language: Optional[constr(min_length=1)] = None
    # Set when github answers a request for this repo with a different name, which means
    # the repo was transferred to another owner. full_name is kept as the name it was
    # requested by (that is how it is cached), and this holds the name it lives at now.
    transferred_to: Optional[str] = None

    @field_validator('created_at', 'pushed_at', mode='before')
    @classmethod
    def parse_date(cls, v):
        return parse(v) if isinstance(v, str) else v

    @field_validator('topics', mode='before')
    @classmethod
    def convert_topics(cls, value):
        return [topic.lower() for topic in value]

    @property
    def identity(self):
        """ Identity of the repo, stable across owner transfers and renames.

        full_name is not an identity: when a repo is transferred (jmorganca/ollama ->
        ollama/ollama) github keeps serving the same repo under both names, so the same
        repo gets cached twice and shown twice in a list. The creation date does survive
        the transfer, down to the second, so it is what groups both copies together.
        """
        return self.created_at

    def is_same_repo_as(self, other) -> bool:
        """ True if both are the same repo under two names (a transfer or a rename).

        Comparing all the metadata is too strict: the two copies were downloaded on
        different days, so stars and push date have drifted apart. Comparing only the
        creation date is too loose: two unrelated repos can be created in the same
        second. So the creation date has to be backed by another field that a transfer
        does not change: the repo name, the description or the language.
        """
        if self.identity != other.identity:
            return False
        same_name = self.full_name.split('/')[-1].lower() == other.full_name.split('/')[-1].lower()
        same_description = bool(self.description) and self.description == other.description
        same_language = bool(self.language) and self.language == other.language
        return same_name or same_description or same_language

    def is_current_name_of(self, other) -> bool:
        """ True if this copy is the name the repo lives at now and the other one is not.

        When a repo succeeds and moves from a user to an organization created for it
        (jmorganca/ollama -> ollama/ollama), the name to keep is the new one. Which one
        it is cannot be guessed from the names, github is the one that tells: asked for
        the old name it answers with the new one, and that answer is what the downloader
        stores in transferred_to.
        """
        return other.transferred_to is not None and not self.transferred_to

    def is_fresher_than(self, other) -> bool:
        """ True if this copy of the repo was captured later than the other one.

        Fallback to pick a survivor for repos cached before transfers started being
        recorded, where nothing says which name is the current one. It only means this
        copy was downloaded later, so its data is the less outdated of the two.
        """
        return (self.pushed_at, self.stargazers_count) > (other.pushed_at, other.stargazers_count)
