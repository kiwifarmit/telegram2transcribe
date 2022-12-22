import hashlib
import json
import logging
import sys
import time
import uuid

import boto3
import pandas as pd
import requests

import mlib.transcribe as transcr


"""
root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)
"""


###


filters = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

session = boto3.Session(profile_name='x')
transcribe = session.client('transcribe', region_name = 'eu-central-1')

for mfilter in filters:
    jobs = transcr.jobs_list(str(mfilter), transcribe)

    for job in jobs:
        print(job['TranscriptionJobName'])
    
    time.sleep(1)

print("Now uniq them")