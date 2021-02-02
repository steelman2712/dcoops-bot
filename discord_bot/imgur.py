from imgurpython import ImgurClient
import os 
from dotenv import load_dotenv
import requests
import ast
import json
import asyncio
import time
url = "https://api.imgur.com/3/upload"

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

client_id = os.environ.get("IMGUR_CLIENT_ID")
client_secret = os.environ.get("IMGUR_CLIENT_SECRET")

async def upload_video(video_file):
    with open("./test2.mp4","rb") as video:
        data = {
            'video': video.read(),
            'type': "file"
        }
        response = requests.post(url=url,files={"video":video},headers={'Authorization': f"Client-ID {client_id}"})
    response = json.loads(response.content)
    data = response.get("data")
    upload_id = data.get("id")
    link = data.get("link")
    link = link.replace("https://","http://")
    print(link)
    processing = data.get("processing").get("status")
    loops = 0
    return link
"""     while processing == "pending":
        if loops < 6:
            print(loops)
            asyncio.wait(2)
            processing_response = requests.get(url=f"https://api.imgur.com/3/image/{upload_id}",headers={'Authorization': f"Client-ID {client_id}"})
            processing_response = json.loads(processing_response.content)
            processing_data = processing_response.get("data")
            processing = processing_data.get("processing").get("status")
            loops += 1 """
    
