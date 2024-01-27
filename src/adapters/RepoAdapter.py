from src.models.RepoModel import RepoModel


class RepoAdapter():
    """ Class to convert from the info returned by
      the GitHub GraphQl to the RepoMetaData class"""
    @staticmethod
    def convert_graphql_to_repo_metadata(repo_data):
        repo_formatted = {}
        repo_formatted["full_name"] = repo_data["nameWithOwner"]
        # if description is None, set it to empty string
        repo_formatted["description"] = repo_data["description"] if repo_data.get("description","") else ""
        repo_formatted["topics"] = [topic["topic"]["name"] for topic in repo_data["repositoryTopics"]["nodes"]]
        repo_formatted["created_at"] = repo_data["createdAt"]
        repo_formatted["pushed_at"] = repo_data["pushedAt"]
        repo_formatted["stargazers_count"] = repo_data["stargazers"]["totalCount"]
        try :
            if repo_data["languages"]["edges"]:
                repo_formatted["language"] = repo_data["languages"]["edges"][0]["node"]["name"]
            else:
                repo_formatted["language"] = "unknown"
        except:
            repo_formatted["language"] = "unknown"
        return RepoModel(**repo_formatted)
