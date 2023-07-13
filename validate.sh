#!/bin/sh -e

# echo '>>> Cleaning cache'
# rm -rf backend/.mypy_cache
# rm -rf backend/.pytest_cache
# rm -rf backend/__pycache__

echo '>>> Running Pylint'
pylint -E -v *.py

echo '>>> Running Mypy'
mypy .

## currently no tests
# echo '>>> Running Pytest'
# pytest -vv --doctest-modules -s backend # --disable-warnings

echo '>>> Running Black'
black .
