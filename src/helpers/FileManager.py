import os
import shutil
import glob
import logging
from tqdm import tqdm
import json
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

    def copy_files(self, source_dir: str, target_dir: str):
        source_dir = os.path.expanduser(source_dir)
        target_dir = os.path.expanduser(target_dir)
        self.logger.info(f"Copying files from {source_dir} to {target_dir}")
        files = glob.glob(f"{source_dir}/*")

        for file in tqdm(files, desc="Copying files", unit="file"):
            if os.path.isfile(file):
                shutil.copy(file, target_dir)
        self.logger.info(f"Finished copying files from {source_dir} to {target_dir}")

    def generate_json_files(self):
        """    Read the data f"{frontend_dir}/public/awesome/", and create a json file with an array with all the files """
        self.logger.info(f"Generating json files in {self.frontend_dir}")
        files = glob.glob(f"{self.frontend_dir}/public/awesome/*")
        links = [os.path.basename(file).replace(".json","").replace("@","/") for file in files if file.endswith(".json")]
        # precede each link with "https://github.com/"
        links = [f"https://github.com/{link}" for link in links]
        links = sorted(links)

        self.logger.info(f"Finished generating json files in {self.frontend_dir} with {len(links)} awesome lists")
        with open(f"{self.frontend_dir}/public/lists.json", "w") as f:
            f.write(json.dumps(links, indent=4))
        self.logger.info(f"Finished generating {self.frontend_dir}/public/lists.json")

    def move_data_frontend_dir(self):
        """ Move the generated data from backend to frontend repos"""
        self.clean_directory(f"{self.frontend_dir}/public/awesome/")
        self.copy_files(f"{self.backend_dir}/var/awesome/", f"{self.frontend_dir}/public/awesome")

        self.clean_directory(f"{self.frontend_dir}/public/topic/")    
        self.copy_files(f"{self.backend_dir}/var/topic/", f"{self.frontend_dir}/public/topic")

        self.generate_json_files()    

    def run(self):
        self.move_data_frontend_dir()