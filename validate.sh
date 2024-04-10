#!/bin/sh -e

# echo '>>> Cleaning cache'
# rm -rf backend/.mypy_cache
# rm -rf backend/.pytest_cache
# rm -rf backend/__pycache__

echo '>>> Running Pylint'
pylint -E -v *.py

echo '>>> Running Mypy'
mypy .

echo '>>> Running Pytest on util.py'
pytest --doctest-modules -s util.py # -vv --disable-warnings

echo '>>> Running Black'
black .

