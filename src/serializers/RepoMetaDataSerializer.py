      

from src.models.RepoModel import RepoModel
from src.models.AwesomeModel import AwesomeModel  
from src.serializers.AbstractSerializer import AbstractSerializer
import json
import os
import time

class RepoMetaDataSerializer(AbstractSerializer):
    """
    Class for serializing and deserializing instances of RepoMetaData to and from a file.

    Methods:
        to_file(repo_meta_data: RepoMetaData, filename: str): Saves an instance of RepoMetaData to a file.
        from_file(filename: str) -> RepoMetaData: Loads an instance of RepoMetaData from a file.
    """
    CATEGORY = "repo"

    # Cuantos dias vale una ficha antes de volver a preguntarle a github.
    #
    # El cache no tenia caducidad: si el fichero existia, se usaba. Un repo
    # guardado hace dos años seguia sirviendo las estrellas y el pushed_at de
    # hace dos años para siempre, y eso envenena el orden por "hot", que
    # divide estrellas entre dias de vida. renew.sh lo arreglaba borrandolo
    # todo, pero obliga a rebajar los 23.000 de una sentada y hay que
    # acordarse de lanzarlo.
    #
    # Con 30 dias y una pasada mensual, cada ficha se refresca una vez por
    # ciclo. Son ~1.200 peticiones GraphQL (van en bloques de 20), muy por
    # debajo del limite de 5.000/h.
    CACHE_MAX_AGE_DAYS = 30


    @staticmethod
    def to_file(repo_meta_data: RepoModel):
        filename_clean = repo_meta_data.full_name.replace('/', '@')
        # Overwrite the file if it already exists
        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename_clean}.json", 'w') as f:
                    f.write(repo_meta_data.model_dump_json())


    @staticmethod
    def from_file(repo_name: str) -> RepoModel:
        filename = repo_name.replace('/', '@')

        with open(f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename}.json") as f:
            data = json.load(f)
        return RepoModel(**data)
    
    @staticmethod
    def exists_file(repo_name:str) -> bool:
        """ True si hay ficha cacheada y todavia es reciente.

        Devolver False para una ficha vieja es lo que hace que quien busca en
        el cache la pida otra vez, sin tener que tocar esa logica.
        """
        # We invoke the static method from the parent class
        if not AbstractSerializer.exists_file(repo_name, RepoMetaDataSerializer.CATEGORY):
            return False

        filename = repo_name.replace('/', '@')
        path = f"./var/{RepoMetaDataSerializer.CATEGORY}/{filename}.json"
        try:
            edad_dias = (time.time() - os.path.getmtime(path)) / 86400
        except OSError:
            return False
        return edad_dias < RepoMetaDataSerializer.CACHE_MAX_AGE_DAYS
