#!/bin/bash

# create python virtual environment
python3 -m venv venv

# activate the virtual environment
source venv/bin/activate

# install dependencies
pip install -r requirements.txt