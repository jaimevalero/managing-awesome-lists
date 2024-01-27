import unittest
from src.categories.AwesomeCategory import AwesomeCategory
import os
from dotenv import load_dotenv

class TestAwesomeCategory(unittest.TestCase):
    def setUp(self):
        # Cargar el token de acceso desde el entorno
        # load .env
        load_dotenv()
        self.access_token = os.getenv("CREDENTIALS")
        self.awesome_list_name = "viatsko/awesome-vscode"

    def test_load_awesome_category(self):
        # Crear una instancia de AwesomeCategory
        awesome_category = AwesomeCategory(self.awesome_list_name, self.access_token)

        # Comprobar que se ha cargado correctamente
        self.assertIsNotNone(awesome_category.repo_meta_data)
        self.assertIsNotNone(awesome_category.repos_data)
        self.assertGreater(len(awesome_category.repos_data), 0)

    def test_serialize_awesome_category(self):
        # Crear una instancia de AwesomeCategory
        awesome_category = AwesomeCategory(self.awesome_list_name, self.access_token)

        # Intentar serializar a un archivo
        try:
            awesome_category.to_file()
        except Exception as e:
            self.fail(f"La serialización falló con el error: {e}")

if __name__ == '__main__':
    unittest.main()