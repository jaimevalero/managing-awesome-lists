<h1>Folders</h1>

<h2>utils</h2>
<blockquote><em>Utility classes for downloading READMEs and repository lists from GitHub.</em></blockquote>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="utils/ReadmeDownloader.py">ReadmeDownloader</a></td>
    <td>A utility class for downloading README files from GitHub repositories.</td>
  </tr>
  <tr>
    <td><a href="utils/RepoListDownloader.py">RepoListDownloader</a></td>
    <td>Class for downloading a list of GitHub repositories.</td>
  </tr>
</table>

<h2>models</h2>
<p><em>Data models for representing awesome lists, topics, categories, and repositories.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="models/AwesomeModel.py">AwesomeModel</a></td>
    <td>This class is for serializing the awesome list only.</td>
  </tr>
  <tr>
    <td><a href="models/AbstractModel.py">AbstractModel</a></td>
    <td>This Base class is for serializing a category.</td>
  </tr>
  <tr>
    <td><a href="models/RepoModel.py">RepoModel</a></td>
    <td>Model for storing metadata of a repository.</td>
  </tr>
  <tr>
    <td><a href="models/TopicModel.py">TopicModel</a></td>
    <td>This class is for serializing the topic list only.</td>
  </tr>
</table>

<h2>adapters</h2>
<p><em>Convert GitHub API responses to internal models and handle RepoModel lists.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="adapters/RepoAdapter.py">RepoAdapter</a></td>
    <td>Converts GitHub GraphQL API responses to RepoModel objects.</td>
  </tr>
  <tr>
    <td><a href="adapters/RepoModelListAdapter.py">RepoModelListAdapter</a></td>
    <td>Manipulates lists of RepoModel objects (deduplication, sorting).</td>
  </tr>
</table>

<h2>categories</h2>
<p><em>Classes representing types of repository groupings, such as awesome lists and topics.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="categories/AbstractCategory.py">AbstractCategory</a></td>
    <td>Base class representing a category of repositories (awesome/topic).</td>
  </tr>
  <tr>
    <td><a href="categories/AwesomeCategory.py">AwesomeCategory</a></td>
    <td>Represents an awesome list containing GitHub repositories.</td>
  </tr>
  <tr>
    <td><a href="categories/TopicCategory.py">TopicCategory</a></td>
    <td>Represents a GitHub topic containing related repositories.</td>
  </tr>
</table>

<h2>downloaders</h2>
<p><em>Components for downloading README files and repository metadata.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="downloaders/RepoDownloader.py">ReadmeDownloader</a></td>
    <td>Downloads README files from GitHub repositories.</td>
  </tr>
  <tr>
    <td><a href="downloaders/RepoDownloader.py">RepoListDownloader</a></td>
    <td>Downloads metadata for lists of GitHub repositories.</td>
  </tr>
</table>

<h2>helpers</h2>
<p><em>Utilities for file operations and processing lists of RepoModel objects.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="helpers/FileManager.py">FileManager</a></td>
    <td>Manages file operations between backend and frontend directories.</td>
  </tr>
  <tr>
    <td><a href="helpers/RepoModelList.py">RepoModelList</a></td>
    <td>Utility functions for processing lists of RepoModel objects.</td>
  </tr>
</table>

<h2>populators</h2>
<p><em>Populate repository lists from awesome-list READMEs or GitHub topics.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="populators/AbstractPopulator.py">AbstractPopulator</a></td>
    <td>Abstract base class for populating repository lists.</td>
  </tr>
  <tr>
    <td><a href="populators/AwesomePopulator.py">AwesomePopulator</a></td>
    <td>Populates repositories from awesome-list READMEs.</td>
  </tr>
  <tr>
    <td><a href="populators/TopicPopulator.py">TopicPopulator</a></td>
    <td>Populates repositories belonging to specific topics.</td>
  </tr>
</table>

<h2>serializers</h2>
<p><em>Serialize and deserialize repository, category, and metadata objects.</em></p>
<table>
  <tr>
    <th>Class Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><a href="serializers/AbstractSerializer.py">AbstractSerializer</a></td>
    <td>Base class for serializing/deserializing repository data.</td>
  </tr>
  <tr>
    <td><a href="serializers/AwesomeSerializer.py">AwesomeSerializer</a></td>
    <td>Serializes/deserializes AwesomeCategory objects.</td>
  </tr>
  <tr>
    <td><a href="serializers/RepoMetaDataSerializer.py">RepoMetaDataSerializer</a></td>
    <td>Handles serialization of individual repository metadata.</td>
  </tr>
  <tr>
    <td><a href="serializers/TopicSerializer.py">TopicSerializer</a></td>
    <td>Serializes/deserializes TopicCategory objects.</td>
  </tr>
</table>

