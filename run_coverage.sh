#!/bin/bash

# Hay que crear aqui un virtual env con python 3.10 y activarlo
conda activate ` basename $PWD`

python -m coverage run -m unittest discover -p test_*.py -s tests
python -m coverage report 
sudo docker run     --rm     -v "${PWD}:/usr/src"     sonarsource/sonar-scanner-cli 
