import logging

# examples modified from AWS documentation

def job_delete(job_name, transcribe_client):
    """
    Deletes a transcription job. This also deletes the transcript associated with
    the job.

    :param job_name: The name of the job to delete.
    :param transcribe_client: The Boto3 Transcribe client.
    """
    try:
        transcribe_client.delete_transcription_job(
            TranscriptionJobName=job_name)
        logging.info("Deleted job %s.", job_name)
    except Exception as err:
        logging.exception("Couldn't delete job %s.", job_name)
        raise


def job_get(job_name, transcribe_client):
    """
    Gets details about a transcription job.

    :param job_name: The name of the job to retrieve.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The retrieved transcription job.
    """
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response  # ['TranscriptionJob']
        logging.info("Got job %s.", job['TranscriptionJob']['TranscriptionJobName'])
    except Exception as err:
        logging.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job


def jobs_list(job_filter, transcribe_client):
    """
    Lists summaries of the transcription jobs for the current AWS account.

    :param job_filter: The list of returned jobs must contain this string in their
                       names.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The list of retrieved transcription job summaries.
    """
    try:
        response = transcribe_client.list_transcription_jobs(
            JobNameContains=job_filter)
        jobs = response['TranscriptionJobSummaries']
        next_token = response.get('NextToken')
        while next_token is not None:
            response = transcribe_client.list_transcription_jobs(
                JobNameContains=job_filter, NextToken=next_token)
            jobs += response['TranscriptionJobSummaries']
            next_token = response.get('NextToken')
        logging.info("Got %s jobs with filter %s.", len(jobs), job_filter)
    except Exception as err:
        logging.exception("Couldn't get jobs with filter %s.", job_filter)
        raise
    else:
        return jobs


def job_start(
        job_name, media_uri, media_format, language_code, transcribe_client,
        vocabulary_name=None):
    """
    Starts a transcription job. This function returns as soon as the job is started.
    To get the current status of the job, call get_transcription_job. The job is
    successfully completed when the job status is 'COMPLETED'.

    :param job_name: The name of the transcription job. This must be unique for
                     your AWS account.
    :param media_uri: The URI where the audio file is stored. This is typically
                      in an Amazon S3 bucket.
    :param media_format: The format of the audio file. For example, mp3 or wav.
    :param language_code: The language code of the audio file.
                          For example, en-US or ja-JP
    :param transcribe_client: The Boto3 Transcribe client.
    :param vocabulary_name: The name of a custom vocabulary to use when transcribing
                            the audio file.
    :return: Data about the job.
    """
    try:
        job_args = {
            'TranscriptionJobName': job_name,
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code}
        if vocabulary_name is not None:
            job_args['Settings'] = {'VocabularyName': vocabulary_name}
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logging.info("Started transcription job %s.", job_name)
    except Exception as err:
        logging.exception("Couldn't start transcription job %s.", job_name)
        raise
    else:
        return job