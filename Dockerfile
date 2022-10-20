FROM python:3.10

ARG USER_ID
ARG GROUP_ID

RUN apt update
RUN apt install -y sox libcurl4-openssl-dev libsox-dev libopencv-dev clang
RUN apt install -y ffmpeg

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install yt-dlp pandas requests scipy progress

RUN addgroup --gid ${GROUP_ID} user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

USER user

COPY . /workdir
WORKDIR /workdir
