import os
import shutil
import glob
import logging
import subprocess
import datetime
from tqdm import tqdm
import json

from src.serializers.AwesomeSerializer import AwesomeSerializer
from src.serializers.SimilarReposSerializer import SimilarReposSerializer
from src.serializers.TopicIndexSerializer import TopicIndexSerializer

# lists.json es la fuente de verdad, escrita a mano. Lo que consume el frontend
# es esto otro: lo mismo mas el nombre para mostrar y la descripcion que llega de
# github. Nombres distintos a proposito, para que se vea cual se edita y cual se
# regenera en cada pasada.
ENRICHED_LISTS_FILE = "lists_enriched.json"
SOURCE_LISTS_FILE = "lists.json"


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
        self.copy_files(f"{self.backend_dir}/{ENRICHED_LISTS_FILE}",
                        f"{self.frontend_dir}/public/{ENRICHED_LISTS_FILE}")

        self.clean_directory(f"{self.frontend_dir}/public/{SimilarReposSerializer.CATEGORY}/")
        self.copy_directories(f"{self.backend_dir}/var/{SimilarReposSerializer.CATEGORY}/",
                              f"{self.frontend_dir}/public/{SimilarReposSerializer.CATEGORY}")

        self.generate_topics_index()
        self.copy_files(f"{self.backend_dir}/{TopicIndexSerializer.INDEX_FILENAME}",
                        f"{self.frontend_dir}/public/{TopicIndexSerializer.INDEX_FILENAME}")

    def generate_topics_index(self):
        """ Build the index the frontend search bar uses to find topics.

        The work belongs to TopicIndexSerializer; here it is only wired into the
        same step that already builds lists.json before copying it over.
        """
        topics = TopicIndexSerializer.from_directory(f"{self.backend_dir}/var/{TopicIndexSerializer.CATEGORY}")
        TopicIndexSerializer.to_file(topics, f"{self.backend_dir}/{TopicIndexSerializer.INDEX_FILENAME}")

    def load_source_icons(self):
        """ El icono de cada lista, indexado por owner/repo en minusculas. """
        ruta = os.path.join(self.backend_dir, SOURCE_LISTS_FILE)
        try:
            with open(ruta, encoding="utf-8") as f:
                entradas = json.load(f)
        except (OSError, ValueError):
            self.logger.warning(f"No se pudo leer {ruta}: las listas saldran sin icono")
            return {}
        iconos = {}
        for entrada in entradas:
            nombre = entrada.get("url", "").replace("https://github.com/", "").rstrip("/")
            if nombre and entrada.get("icon"):
                iconos[nombre.lower()] = entrada["icon"]
        return iconos

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
        # El icono lo pone la fuente de verdad; el frontend solo lo pinta, y ya no
        # necesita saber que lista es cual.
        iconos = self.load_source_icons()
        index_json_contents = [
            {
                'category_name': awesome_list.category_name,
                'description': awesome_list.repo_meta_data.description,
                'display': awesome_list.category_name.split("/")[1].lower().replace("awesome-",""),
                'icon': iconos.get(awesome_list.category_name.lower(), '')
            } for awesome_list in awesome_lists]
        # sort index_json_contents by key display
        index_json_contents = sorted(index_json_contents, key=lambda k: k['display'])
        with open(f"{self.backend_dir}/{ENRICHED_LISTS_FILE}", "w") as f:
            f.write(json.dumps(index_json_contents, indent=4))

    def git(self, *args, check=True):
        """ Corre un comando git en el repo del frontend y devuelve su salida. """
        result = subprocess.run(
            ["git", "-C", self.frontend_dir, *args],
            capture_output=True, text=True
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
        return result.stdout.strip()

    def publish_frontend(self):
        """ Sube al frontend los datos que se acaban de copiar.

        Sin esto la cadena se corta justo al final: el cron regenera todo y lo
        deja en el disco, pero hasta que alguien no hace push a mano Vercel no
        construye, asi que la web sigue sirviendo los datos del mes pasado.

        No revienta el ciclo si algo va mal: los datos ya estan copiados y el
        push se puede repetir a mano. Solo se avisa en el log.
        """
        try:
            rama = self.git("rev-parse", "--abbrev-ref", "HEAD")
            if rama not in ("master", "main"):
                self.logger.warning(f"El frontend esta en la rama {rama}: no se publica")
                return

            if not self.git("status", "--porcelain"):
                self.logger.info("El frontend no tiene cambios: no hay nada que publicar")
                return

            self.git("add", "-A")
            fecha = datetime.date.today().isoformat()
            self.git("commit", "-m", f"Monthly update {fecha}")

            # Alguien pudo tocar el frontend entre medias; sin esto el push se
            # rechaza y los datos se quedan sin publicar.
            self.git("pull", "--rebase", "--autostash", "origin", rama)
            self.git("push", "origin", rama)
            self.logger.info(f"Frontend publicado en {rama}: Vercel construira solo")
        except Exception as error:
            self.logger.error(f"No se pudo publicar el frontend: {error}")

    def run(self):
        self.move_data_frontend_dir()
        self.publish_frontend()

# main
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    backend_dir = "~/git/managing-awesome-lists"
    frontend_dir = "~/git/managing-awesome-lists-frontend"
    file_manager = FileManager(backend_dir, frontend_dir)
    file_manager.run()        