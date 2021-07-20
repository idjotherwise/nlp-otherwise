#!/bin/sh
set -e
cd $(dirname "$0")/..
cd src/

python3 update_datasets.py && git add ../data_sets