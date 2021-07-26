import os
from dotenv import load_dotenv
from discord.ext import commands
from pretty_help import PrettyHelp

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

import sys

sys.path.append(os.path.abspath(os.path.join(".", "discord_bot")))
sys.path.append(os.path.abspath(os.path.join(".", "face-swap")))
from music import Music
from files import Files
from utilities import Utilities
from activity import Resident
from groans import Groans
from jigsaw import Jigsaw
from events import Events


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description="DCoops bot",
    case_insensitive=True,
    help_command=PrettyHelp(),
)


@bot.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(bot.user))
    print("------")


token = os.environ.get("DISCORD_TOKEN")
bot.add_cog(Music(bot))
bot.add_cog(Files(bot))
bot.add_cog(Utilities(bot))
bot.add_cog(Resident(bot))
bot.add_cog(Groans(bot))
bot.add_cog(Jigsaw(bot))
bot.add_cog(Events(bot))
bot.run(token)
