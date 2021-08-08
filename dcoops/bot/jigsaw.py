import dcoops.bot.imgur
from discord.ext import commands

import requests
import shutil
from bs4 import BeautifulSoup

JIGSAW_ERROR_MESSAGE = "Unable to create jigsaw"
JIGSAW_EXPLORER_URL = "	https://www.jigsawexplorer.com/jigsaw-puzzle-result/"


class Jigsaw(commands.Cog):
    @commands.command()
    async def jigsaw(self, ctx, number_of_pieces=500):
        try:
            discord_url = ctx.message.attachments[0].url
            image_filename = await self.download_image(discord_url)
            imgur_link = await imgur.upload_image(image_filename)
            jigsaw_url = await self.create_jigsaw(imgur_link, number_of_pieces)
            print("Jigsaw url: ", jigsaw_url)
            await ctx.send(jigsaw_url)
        except Exception as e:
            print(e)
            await ctx.send(JIGSAW_ERROR_MESSAGE)

    async def download_image(self, discord_url):
        image_filename = discord_url.split("/")[-1]
        r = requests.get(discord_url, stream=True)
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True
            with open(image_filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            return image_filename
        else:
            raise ValueError("Unable to download image from discord")

    async def create_jigsaw_data(self, imgur_link, number_of_pieces):
        json_data = {
            "image-url": imgur_link,
            "credit-line": "",
            "credit-url": "",
            "puzzle-nop": number_of_pieces,
            "color": "blue",
        }
        return json_data

    async def create_jigsaw(self, imgur_link, number_of_pieces):
        json_data = await self.create_jigsaw_data(imgur_link, number_of_pieces)
        print(json_data)
        r = requests.post(JIGSAW_EXPLORER_URL, data=json_data)
        jigsaw_page = r.content
        soup = BeautifulSoup(jigsaw_page)
        jigsaw_url = soup.find(id="short-link").get("value")
        print(jigsaw_url)
        return jigsaw_url
