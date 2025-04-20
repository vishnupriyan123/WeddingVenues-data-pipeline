#!/bin/bash

cd "$(dirname "$0")"
source ../venv/bin/activate
python cleaner.py >> ../logs/cleaner_log.txt 2>&1