import unittest
import os

class TestDirectories(unittest.TestCase):
    def test_directories_exist(self):
        self.assertTrue(os.path.isdir('var/'))
        self.assertTrue(os.path.isdir('var/repo'))
        self.assertTrue(os.path.isdir('var/topics'))
        self.assertTrue(os.path.isdir('var/awesome'))

if __name__ == '__main__':
    unittest.main()