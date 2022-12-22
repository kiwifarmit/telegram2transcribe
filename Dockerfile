FROM python:3.11-slim
WORKDIR /app
ADD ./requirements.txt .

RUN apt-get --fix-missing update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y ffmpeg

RUN pip3 install -r requirements.txt

# docker build -t carlok/transcribe:0.2 .
# clear; docker run -it -v $HOME/.aws/credentials:/root/.aws/credentials -v $PWD:/app carlok/transcribe:0.2 python3 bot.py