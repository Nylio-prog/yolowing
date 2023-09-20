#!/bin/bash

# create python virtual environment
python -m venv -p python3.10 yolowing

# activate the virtual environment
source yolowing/bin/activate

# install dependencies
pip install -r requirements.txt