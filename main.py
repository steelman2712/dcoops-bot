import os 
from dotenv import load_dotenv
from discord.ext import commands

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

import sys
sys.path.append(os.path.abspath(os.path.join('.', 'discord_bot')))

from music import Music
from files import Files

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='Relatively simple music bot example')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')



token = os.environ.get("DISCORD_TOKEN")
bot.add_cog(Music(bot))
bot.add_cog(Files(bot))
bot.run(token)

