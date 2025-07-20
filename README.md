# Awesome List Viewer

[Live Demo](https://managing-awesome-lists.vercel.app/)

**Awesome List Viewer** is a backend utility for discovering and managing GitHub "awesome lists". It downloads metadata about curated awesome lists from GitHub, stores the data as JSON, and makes it available for querying through a dedicated frontend application.

---

## Features

- **Automated Extraction:** Parses a configurable list of GitHub awesome lists, and extracts metadata (description, topics, stars, language, etc.) from each repository found.
- **Efficient Storage:** Saves awesome list and repository metadata in structured JSON files, optimized for fast querying.
- **Topic Categorization:** Groups repositories by topics for easier discovery.
- **Frontend Integration:** Designed to power [the frontend app](https://managing-awesome-lists.vercel.app/) for user-friendly browsing and search.
- **Easy Updates:** Can refresh all data with a single run, using your GitHub API token.

---

## How It Works

1. **Fetch Awesome Lists:** The backend reads a list of awesome GitHub repositories from [`lists.txt`](lists.txt).
2. **Download Metadata:** For each awesome list, it fetches the README, extracts repositories, and downloads metadata (stars, topics, etc.) via the GitHub API.
3. **Store as JSON:** Metadata is saved in the `var/` directory (`var/awesome/`, `var/repo/`, `var/topic/`).
4. **Frontend Consumption:** The generated JSON files are intended to be copied to the frontend repo (`managing-awesome-lists-frontend`) for browsing and querying.

---

## Directory Structure

```
.
├── app.py                 # Main entry point: generates awesome lists and topic categories
├── lists.txt              # List of awesome lists (one per line, GitHub URLs)
├── requirements.txt       # Python dependencies
├── var/                   # Generated JSON data (awesome lists, topics, repos)
├── src/                   # Source code
│   ├── categories/        # Category logic (Awesome, Topic)
│   ├── downloaders/       # Tools for fetching repo/readme data
│   ├── helpers/           # File management, utils
│   ├── models/            # Data models (Awesome, Topic, Repo)
│   ├── populators/        # Populator logic for awesome lists, topics
│   └── serializers/       # Serialization/deserialization logic
└── tests/                 # Unit tests
```

---

## Usage

### 1. Prerequisites

- Python 3.10+
- A GitHub API access token (for higher rate limits and private repo access)
- `pip install -r requirements.txt`
- Create a `.env` file with:  
  ```
  CREDENTIALS=your_github_token_here
  ```

### 2. Running the Backend

```bash
python app.py
```

- This will:
  - Parse the lists in `lists.txt`
  - Download metadata for each awesome list and its repositories
  - Generate JSON files in `var/`
  - Move/copy the relevant data to the frontend directory (as configured in `FileManager`)

### 3. Connecting to the Frontend

The data is meant for the [Awesome List Viewer frontend](https://github.com/jaimevalero/managing-awesome-lists-frontend).  
After running the backend, the JSON files are copied to the frontend's `public/` directory for use in the web app.

---

## Example: Adding a New Awesome List

1. Add the GitHub URL to `lists.txt` (one URL per line).
2. Run `python app.py` again to update the dataset.

---

## Data Model

Each repository entry includes:

- `full_name` – owner/repo
- `description`
- `topics` – list of topics
- `created_at`, `pushed_at`
- `stargazers_count`
- `language`

Awesome lists and topics are grouped and serialized for efficient frontend querying.

---

## Development

- All logic is modularized in `src/` (see [src/README.md](src/README.md) for details).
- Unit tests are provided in `tests/`.
- Linting and type checking are recommended for code quality.

### Run tests

```bash
python -m unittest discover -s tests
```

---

## Contributing

Pull requests and issues are welcome!  
If you'd like to add new features or improve the code, please fork the repo and submit a PR.

---

## License

This project is released under the MIT License.

---

**Discover and explore the best GitHub resources with Awesome List Viewer!**

---

Let me know if you want the README in another format (Markdown table, shorter version, etc.) or want to focus on a specific section.
