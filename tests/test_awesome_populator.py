import unittest
from src.populators.AwesomePopulator import AwesomePopulator
import os
from dotenv import load_dotenv
from src.models.RepoModel import RepoModel 

class TestAwesomePopulator(unittest.TestCase):
    def setUp(self):
        load_dotenv()
        self.access_token = os.getenv("CREDENTIALS")        
        self.awesome_list_name = "sindresorhus/awesome"
        self.populator = AwesomePopulator(self.access_token, self.awesome_list_name)

    def test_populate(self):
        repo_models = self.populator.populate()
        self.assertIsInstance(repo_models, list)  # Comprueba que se devuelve una lista
        # Comprueba que todos los elementos de la lista son instancias de RepoModel
        self.assertTrue(all(isinstance(model, RepoModel) for model in repo_models))

if __name__ == "__main__":
    unittest.main()
