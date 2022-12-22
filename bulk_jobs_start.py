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

f = open('x.json')
data = json.load(f)

session = boto3.Session(profile_name='x')
transcribe = session.client('transcribe', region_name = 'eu-central-1')

for i in data:
    job_name = str(uuid.uuid4().int)
    job = transcr.job_start(
        str(uuid.uuid4().int),
        f"s3://x/{i}",
        'mp3',
        'it-IT',
        transcribe
    )
    j_out = {"file": i, "job_name": job_name, "job_id": job['TranscriptionJobName']}
    print(f"{json.dumps(j_out)},")
    time.sleep(1)
