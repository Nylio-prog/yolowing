#!/bin/bash

# create python virtual environment
python -m venv yolowing

# activate the virtual environment
source yolowing/bin/activate

# install dependencies
pip install -r requirements.txt