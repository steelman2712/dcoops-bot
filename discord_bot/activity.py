import discord
from discord.ext import commands

class Resident(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):   
        activity = discord.Activity(name='Resident Evil: The Final Chapter', type=discord.ActivityType.watching)
        await self.client.change_presence(activity=activity)

def setup(client):
    client.add_cog(OnReady(client))