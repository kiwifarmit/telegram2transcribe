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


session = boto3.Session(profile_name='x')
transcribe = session.client('transcribe', region_name = 'x')

f = open('x.json')
data = json.load(f)

for job in data:
    job_id = str(job['job_id'])
    job_result = transcr.job_get(job_id, transcribe)

    transcript_file_uri = job_result['TranscriptionJob']['Transcript']['TranscriptFileUri']

    r = requests.get(transcript_file_uri)
    result = r.json()
    print(f"\n=== {job['file']} => {str(job['job_name'])} => {str(job['job_id'])}")
    print(result['results']['transcripts'][0]['transcript'])

    time.sleep(1)