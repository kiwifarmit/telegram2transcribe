from datetime import datetime

import uuid


def filename_set():
    now = datetime.now()
    date_today = now.strftime("%Y_%m_%d")
    date_time_str = now.strftime("%Y_%m_%d_%H_%M_%S")

    return date_today, f"{date_time_str}_{uuid.uuid4().int}"