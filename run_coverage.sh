#!/bin/bash
coverage run -m unittest discover -p test_*.py -s tests
coverage report
