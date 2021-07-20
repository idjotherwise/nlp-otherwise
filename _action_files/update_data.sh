#!/bin/sh
set -e
cd $(dirname "$0")/..
cd src/

curl "https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline.csv" -o ../data_sets/CovidFaelle_Timeline.csv
curl "https://covid19-dashboard.ages.at/data/CovidFallzahlen.csv" -o ../data_sets/CovidFallzahlen.csv

python3 update_datasets.py && git add ../data_sets