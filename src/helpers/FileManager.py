import os
import shutil
import glob
import logging
from tqdm import tqdm
import json

from src.serializers.AwesomeSerializer import AwesomeSerializer

class FileManager:
    def __init__(self, backend_dir: str, frontend_dir: str):
        self.backend_dir = os.path.expanduser(backend_dir)
        self.frontend_dir = os.path.expanduser(frontend_dir)
        self.logger = logging.getLogger(__name__)

    def clean_directory(self, directory_path: str):
        directory_path = os.path.expanduser(directory_path)
        self.logger.info(f"Remove files from {directory_path}")
        shutil.rmtree(directory_path, ignore_errors=True)
        os.makedirs(directory_path, exist_ok=True)

    def copy_directories(self, source_dir: str, target_dir: str):
        source_dir = os.path.expanduser(source_dir)
        target_dir = os.path.expanduser(target_dir)
        self.logger.info(f"Copying files from {source_dir} to {target_dir}")
        files = glob.glob(f"{source_dir}/*")

        for file in tqdm(files, desc="Copying files", unit="file"):
            if os.path.isfile(file):
                shutil.copy(file, target_dir)
        self.logger.info(f"Finished copying files from {source_dir} to {target_dir}")

    def copy_files(self, source_filename: str, target_filename: str):
        source_filename = os.path.expanduser(source_filename)
        target_filename = os.path.expanduser(target_filename)
        self.logger.info(f"Copying file from {source_filename} to {target_filename}")
        shutil.copy(source_filename, target_filename)
        self.logger.info(f"Finished copying file from {source_filename} to {target_filename}")

    def move_data_frontend_dir(self):
        """ Move the generated data from backend to frontend repos"""
        self.clean_directory(f"{self.frontend_dir}/public/awesome/")
        self.copy_directories(f"{self.backend_dir}/var/awesome/", f"{self.frontend_dir}/public/awesome")

        self.clean_directory(f"{self.frontend_dir}/public/topic/")    
        self.copy_directories(f"{self.backend_dir}/var/topic/", f"{self.frontend_dir}/public/topic")

        self.generate_json_files()    
        self.copy_files(f"{self.backend_dir}/lists.json", f"{self.frontend_dir}/public/lists.json")

    def generate_json_files(self):
        # Read all the yaml files from the /var/awesome/directory, as AwesomeCategory
        read_directory = "f{self.frontend_dir}/public/awesome/"
        awesome_lists = []
        awesome_path ="./var/awesome"
        filenames = os.listdir(awesome_path)

        for filename in filenames:
            has_correct_filename = filename.endswith(".json") and "@" in filename
            if has_correct_filename :
                awesome_list = AwesomeSerializer.from_file(f"{awesome_path}/{filename}")
                has_repos = len(awesome_list.repos_data) > 0
                if has_repos:
                    awesome_lists.append(awesome_list)
        index_json_contents = [ 
            { 
                'category_name': awesome_list.category_name,
                'description': awesome_list.repo_meta_data.description,
                'display': awesome_list.category_name.split("/")[1].lower().replace("awesome-","")
            } for awesome_list in awesome_lists]
        # sort index_json_contents by key display
        index_json_contents = sorted(index_json_contents, key=lambda k: k['display'])
        with open(f"{self.backend_dir}/lists.json", "w") as f:
            f.write(json.dumps(index_json_contents, indent=4))

    def run(self):
        self.move_data_frontend_dir()

# main
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    backend_dir = "~/git/managing-awesome-lists"
    frontend_dir = "~/git/managing-awesome-lists-frontend"
    file_manager = FileManager(backend_dir, frontend_dir)
    file_manager.run()        