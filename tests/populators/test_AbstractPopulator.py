import unittest
from unittest.mock import Mock
from src.models.RepoModel import RepoModel
from src.populators.AbstractPopulator import AbstractPopulator

class TestAbstractPopulator(unittest.TestCase):
    def setUp(self):
        self.populator = AbstractPopulator("access_token", "name")

    def test_init(self):
        self.assertEqual(self.populator.name, "name")
        self.assertEqual(self.populator.access_token, "access_token")
        self.assertIsNone(self.populator.repos_data)
        self.assertEqual(self.populator.current_index, 0)

    def test_iter(self):
        self.populator.repos_data = [RepoModel(), RepoModel()]
        self.assertEqual(list(iter(self.populator)), self.populator.repos_data)

    def test_next(self):
        self.populator.repos_data = [RepoModel(), RepoModel()]
        self.assertEqual(next(self.populator), self.populator.repos_data[0])
        self.assertEqual(next(self.populator), self.populator.repos_data[1])
        with self.assertRaises(StopIteration):
            next(self.populator)

    def test_populate_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.populator.populate()

    def test_normalize(self):
        mock_repo1 = Mock(spec=RepoModel)
        mock_repo2 = Mock(spec=RepoModel)
        self.populator.repos_data = [mock_repo1, mock_repo2]
        normalized_data = self.populator.normalize(self.populator.repos_data)
        self.assertEqual(normalized_data, self.populator.repos_data)

if __name__ == '__main__':
    unittest.main()