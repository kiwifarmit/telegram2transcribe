import logging

from urllib.parse import urlparse


def chat_text_send(http, bot_api_prefix, bot_token, bot_chatID, bot_message):
    try:
        send_text = bot_api_prefix + bot_token + \
        '/sendMessage?chat_id=' + str(bot_chatID) + '&text=' + \
            urlparse(bot_message).geturl()

        response = http.request('GET', send_text)
        logging.info(response.status)

        return # response.json()
    except Exception as e:
        # TODO send mail
        logging.error('exception at telegram: {} - {}'.format(str(e), bot_message))
