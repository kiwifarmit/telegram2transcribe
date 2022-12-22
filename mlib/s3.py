import logging

def upload_file(audio_mp3, today, s3_client, config):
    with open(f"./{audio_mp3}", "rb") as f:
        m_key = f"{today}/{audio_mp3}"
        logging.info(f"s3 upload file errors returned: {s3_client.upload_fileobj(f, config['aws']['s3']['bucket'], m_key)}")

        return m_key


def upload_string(s3_client, mstring, config, today, audio_txt):
    s3_client.put_object(
        Body=mstring, 
        Bucket=config['aws']['s3']['bucket'], 
        Key=f"{today}/{audio_txt}"
    )
