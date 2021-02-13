import os 
from dotenv import load_dotenv
from discord.ext import commands

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

import sys
sys.path.append(os.path.abspath(os.path.join('.', 'discord_bot')))
sys.path.append(os.path.abspath(os.path.join('.', 'face-swap')))
from music import Music
from files import Files
from utilities import Utilities
from activity import Resident
from face_swap import FaceSwap
from groans import Groans




bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),
                   description='DCoops bot', case_insensitive=True)


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('------')



token = os.environ.get("DISCORD_TOKEN")
bot.add_cog(Music(bot))
bot.add_cog(Files(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Resident(bot))
bot.add_cog(FaceSwap(bot))
bot.add_cog(Groans(bot))
bot.run(token)
