
<h2>src/utils</h2>

<p>This folder contains utility classes such as <a href="src/utils/ReadmeDownloader.py">ReadmeDownloader</a> for downloading README files from GitHub repositories, and <a href="src/utils/RepoListDownloader.py">RepoListDownloader</a> for downloading a list of GitHub repositories.</p>

<h2>src/models</h2>

<p>This folder defines all the model classes used in the project. These include <a href="src/models/AwesomeModel.py">AwesomeModel</a> for serializing awesome lists, <a href="src/models/AbstractModel.py">AbstractModel</a> for serializing a category, <a href="src/models/RepoModel.py">RepoModel</a> for storing metadata of a repository, and <a href="src/models/TopicModel.py">TopicModel</a> for serializing the topic list.</p>

<h2>src/controllers</h2>

<p>This folder contains classes that handle the business logic of the project. These include <a href="src/controllers/RepoModelListAdapter.py">RepoModelListAdapter</a> for manipulating lists of RepoModel objects, <a href="src/controllers/RepoAdapter.py">RepoAdapter</a> for converting from the info returned by the GitHub GraphQl to the RepoMetaData class, and <a href="src/controllers/TopicPopulator.py">TopicPopulator</a> and <a href="src/controllers/AwesomePopulator.py">AwesomePopulator</a> for extracting repos from a list of repos that have a given topic or awesome list.</p>

<h2>src/serializers</h2>

<p>This folder contains classes for serializing and deserializing instances of various models to and from a file. These include <a href="src/serializers/TopicSerializer.py">TopicSerializer</a> for TopicModel objects, <a href="src/serializers/RepoMetaDataSerializer.py">RepoMetaDataSerializer</a> for RepoMetaData instances, <a href="src/serializers/AbstractSerializer.py">AbstractSerializer</a> for RepoModel objects, and <a href="src/serializers/AwesomeSerializer.py">AwesomeSerializer</a> for AwesomeModel objects.</p>

<h2>src/categories</h2>

<p>This folder contains classes that represent a category of repositories. These include <a href="src/categories/AwesomeCategory.py">AwesomeCategory</a> for an awesome list in GitHub, <a href="src/categories/AbstractCategory.py">AbstractCategory</a> for an abstract base class that represents a category of repositories, and <a href="src/categories/TopicCategory.py">TopicCategory</a> for a given topic in GitHub.</p>

