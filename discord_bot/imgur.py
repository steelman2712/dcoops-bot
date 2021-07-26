from imgurpython import ImgurClient
import os
from dotenv import load_dotenv
import requests
import ast
import json
import asyncio
import time

url = "https://api.imgur.com/3/upload"

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

client_id = os.environ.get("IMGUR_CLIENT_ID")
client_secret = os.environ.get("IMGUR_CLIENT_SECRET")

TIMEOUT_TIME = 15
TIMEOUT_CHECKS = 5


async def wait_until_processed(upload_id, client_id):
    loops = 0
    processing = "processing"
    while processing != "completed" and loops < 6:
        print(loops)
        await asyncio.sleep(3)
        processing_response = requests.get(
            url=f"https://api.imgur.com/3/image/{upload_id}",
            headers={"Authorization": f"Client-ID {client_id}"},
        )
        processing_response = json.loads(processing_response.content)
        success = processing_response.get("success")
        if success == False:
            break
        else:
            processing_data = processing_response.get("data")
            processing = processing_data.get("processing").get("status")
            loops += 1
            print(processing)
    return True


async def upload_video(video_file):
    with open("./test2.mp4", "rb") as video:
        data = {"video": video.read(), "type": "file", "disable_audio": 1}
        response = requests.post(
            url=url,
            files={"video": open(video_file, "rb")},
            headers={"Authorization": f"Client-ID {client_id}"},
            data=data,
        )
    response = json.loads(response.content)
    data = response.get("data")
    upload_id = data.get("id")
    link = data.get("link")
    link = link.replace("https://i.imgur", "http://imgur")
    print(link)
    await wait_until_processed(upload_id, client_id)
    return link


async def upload_image(image_file):
    with open(image_file, "rb") as image:
        data = {
            "image": image.read(),
            "type": "file",
        }
        response = requests.post(
            url=url,
            files={"image": open(image_file, "rb")},
            headers={"Authorization": f"Client-ID {client_id}"},
            data=data,
        )
    response = json.loads(response.content)
    data = response.get("data")
    upload_id = data.get("id")
    link = data.get("link")
    link = link.replace("https://i.imgur", "http://imgur")
    print(link)
    return link
