#!/bin/bash
coverage run -m unittest discover -p test_*.py -s tests
coverage report

# python -m coverage run -m unittest discover -p test_*.py -s tests
# python -m coverage report 
sudo docker run     --rm     -v "${PWD}:/usr/src"     sonarsource/sonar-scanner-cli 