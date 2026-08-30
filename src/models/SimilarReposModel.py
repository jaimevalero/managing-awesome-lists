from typing import List, Optional

from pydantic import BaseModel

from src.models.RepoModel import RepoModel
from src.models.SimilarRepoModel import SimilarRepoModel


class SimilarReposModel(BaseModel):
    """ This class is for serializing the repos similar to a given repo.

    One of these is written per repo, so the frontend can fetch just the neighbours of
    the repo the reader asked about instead of a table of all of them.

    It has the same shape as a category (a topic, an awesome list): same field names,
    same meaning. That is not a coincidence, it is the point. The frontend route
    /a-<type>/<name> is generic, so a file shaped like this at public/similar/ turns
    into a full page at /a-similar/<owner@repo> -- with its search box, its Hot/Top/New
    order and its pagination -- without a line of frontend code. And since that page
    paints the same card as every other page, and the card carries the button that
    opens the similar repos of ITS repo, the reader can jump from neighbour to
    neighbour without ever reaching an end.

    Attributes:
        category_type (str): Always "similar". It has to match the directory the file
            is served from, because that is what the generic route builds its fetch
            from.
        category_name (str): Full name of the repository these are similar to.
        repos_data (list[SimilarRepoModel]): Its most similar repos, best first.
        frecuent_topics (dict): The most common topics among them, which is what the
            page shows as "related topics": a name for the neighbourhood the reader
            just walked into.
        repo_meta_data (RepoModel): The origin repo itself. Named like the field an
            awesome list uses for the same thing, so the generic page picks up its
            description with no code of its own. Its topics are what every card is
            compared against to say why it is being suggested, which with twelve cards
            and a reader hopping from one to the next is the only thing there is to
            choose a hop by.
    """
    category_type: str = "similar"
    category_name: str
    repos_data: List[SimilarRepoModel]
    frecuent_topics: dict = {}
    repo_meta_data: Optional[RepoModel] = None
