FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /discord

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements2.txt
EXPOSE 80
COPY . .
ENTRYPOINT ["python3", "-u", "./main.py"]
