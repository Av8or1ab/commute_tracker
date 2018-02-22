#!/bin/bash

#source "/home/danielorf/commute_tracker/venv/bin/activate"

nohup /home/danielorf/commute_tracker/venv/bin/python /home/danielorf/commute_tracker/data_collection.py &
cd /home/danielorf/commute_tracker
sudo /home/danielorf/commute_tracker/venv/bin/gunicorn --workers=4 --bind=0.0.0.0:80 ct_server:app &
