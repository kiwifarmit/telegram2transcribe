import certifi
import json
import logging
import os
import time
import urllib3
import uuid

from urllib.parse import urlparse

import boto3
import requests

from jsonc_parser.parser import JsoncParser
from pydub import AudioSegment
from telegram import Update
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters

from mlib import s3, utils

import mlib.telegram as tlgrm
import mlib.transcribe as transcr

def voice_get(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    user = update.message.from_user

    if chat_id != config['telegram']['chat']['input_id']:
        logging.info(f"Audio from unauthorized chat {chat_id}")
        return

    s3_client = boto3.client(
        's3',
        aws_access_key_id = config['aws']['key']['access_id'],
        aws_secret_access_key = config['aws']['key']['secret_access'],
        region_name = config['aws']['region_name']
    )
    session = boto3.Session(profile_name=config['aws']['profile_name'])
    transcribe = session.client('transcribe', region_name = config['aws']['region_name'])


    today, audio_prefix = utils.filename_set()
    audio_ogg = f"{audio_prefix}.ogg"
    audio_mp3 = f"{audio_prefix}.mp3"
    audio_txt = f"{audio_prefix}.txt"

    new_file = context.bot.get_file(update.message.voice.file_id)
    new_file.download(f"{audio_ogg}")
    # update.message.reply_text('Voice note saved')
    AudioSegment.from_file(audio_ogg).export(f"{audio_mp3}", format="mp3")

    m_key = s3.upload_file(audio_mp3, today, s3_client, config)

    os.remove(audio_ogg)
    os.remove(audio_mp3)
    logging.info(f"{audio_mp3} => {m_key}")

    job_name = str(uuid.uuid4().int)
    job = transcr.job_start(
        str(uuid.uuid4().int),
        f"s3://{config['aws']['s3']['bucket']}/{today}/{audio_mp3}",
        'mp3',
        'it-IT',
        transcribe
    )

    job_out = {"file": audio_mp3, "job_name": job_name, "job_id": job['TranscriptionJobName']}
    logging.info(f"{json.dumps(job_out)},")

    while True:
        time.sleep(config['transcribe']['sleep'])
        job_id = str(job_out['job_id'])
        job_result = transcr.job_get(job_id, transcribe)
        if job_result['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            if job_result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                transcript_file_uri = job_result['TranscriptionJob']['Transcript']['TranscriptFileUri']
                r = requests.get(transcript_file_uri)
                result = r.json()
                logging.info(f"=== {job_out['file']} => {str(job_out['job_name'])} => {str(job_out['job_id'])}")
                mstring = f"👨‍🔧 {user['first_name']} {user['last_name']} ➡️  {result['results']['transcripts'][0]['transcript']}"
                logging.info(mstring)
                tlgrm.chat_text_send(http, config['telegram']['bot']['api_prefix'], config['telegram']['bot']['token'], config['telegram']['chat']['output_id'], mstring)
                s3.upload_string(s3_client, mstring, config, today, audio_txt)
                transcr.job_delete(job_out['job_id'], transcribe)
                break
            else:
                logging.error(f"JOB {job_id} FAILED")
                transcr.job_delete(job_out['job_id'], transcribe)
                break
        else:
            logging.info(f"JOB {job_id} is still being processed")


#
#
#


if __name__ == "__main__":
    try:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("debug.log"),
                logging.StreamHandler()
            ]
        )

        config = JsoncParser.parse_file('config.jsonc')

        cert_reqs = "CERT_REQUIRED"
        ca_certs = certifi.where()
        retries = urllib3.Retry(3, redirect=2)
        timeout = 10.0

        http = urllib3.PoolManager(
                cert_reqs=cert_reqs,
                ca_certs=ca_certs,
                retries=urllib3.Retry(3, redirect=2),
                timeout=10.0
        )

        updater = Updater(config['telegram']['bot']['token'])
        updater.dispatcher.add_handler(MessageHandler(Filters.voice , voice_get))
        updater.start_polling()
        updater.idle()
    except Exception as err:
        logging.critical(err)
        raise Exception(err)