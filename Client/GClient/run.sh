#!/bin/sh
export FLASK_APP=GClient.py
export FLASK_ENV=deployment
python3 -m flask run -p 30000
