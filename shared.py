import wordreplacer
import butt_timeout
import discord_comms
import butt_database
from butt_statistics import ButtStatistics
from config import *
import butt_config
import logging
from discord.ext.commands import Bot
import aiohttp
import asyncio
import discord

intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.emojis_and_stickers = True

bot = Bot(description="a bot for farts", command_prefix=command_prefix, pm_help=False, intents=intents)

log = logging.getLogger('bot.' + __name__)

# database instances
db = {
    "minecraft": butt_database.Db(db_server, minecraft_db, db_secrets[0], db_secrets[1]),
    "buttbot": butt_database.Db(db_server, discordbot_db, db_secrets[0], db_secrets[1]),
    "statistics": butt_database.Db(db_server, discordbot_db, db_secrets[0], db_secrets[1])
}

tables = {
    "previously seen": "previously_seen_players",
    "NSA POI": "NSA_POI",
    "NSA": "NSA_module",
    "deaths": "deaths",
    "playertracker": "playertracker_v2"
}

stat_module = ButtStatistics(db["statistics"])
comms_instance = discord_comms.DiscordComms()
shitpost = wordreplacer.WordReplacer(stat_module)
timer_instance = butt_timeout.Timeout()

guild_configs = butt_config.Config()


async def create_http_session():
    session = aiohttp.ClientSession()
    return session


http_session = asyncio.get_event_loop().run_until_complete(create_http_session())
