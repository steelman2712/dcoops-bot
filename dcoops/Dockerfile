FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3-pip \
    ffmpeg \
    build-essential \
    cmake \
    mariadb-client \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /discord

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 80
ENTRYPOINT ["python3", "-u", "./dcoops/main.py"]
