#!/bin/bash

source .tox/release/bin/activate
pip wheel -w wheels .
rm -rf artifacts
mkdir artifacts
mv wheels/importlib_metadata*.whl artifacts/
python setup.py sdist
mv dist/importlib_metadata*.tar.gz artifacts/
rm -rf wheels dist
