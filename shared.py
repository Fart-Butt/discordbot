import wordreplacer
import butt_timeout
import discord_comms
import butt_database
from phraseweights import PhraseWeights
from butt_statistics import ButtStatistics
from config import *
import butt_config
import logging
import vacuum
from discord.ext.commands import Bot
import aiohttp
import asyncio

import spacy

bot = Bot(description="a bot for farts", command_prefix="&", pm_help=False)

log = logging.getLogger('bot.' + __name__)

# database instances
db = {
    "minecraft": butt_database.Db(minecraft_db, db_secrets[0], db_secrets[1]),
    "buttbot": butt_database.Db(discordbot_db, db_secrets[0], db_secrets[1]),
    "statistics": butt_database.Db(discordbot_db, db_secrets[0], db_secrets[1])
}

tables = {
    "previously seen": "previously_seen_players",
    "NSA POI": "NSA_POI",
    "NSA": "NSA_module",
    "deaths": "deaths",
    "playertracker": "playertracker_v2"
}

nlp = spacy.load('en_core_web_lg')
phrase_weights = PhraseWeights(db["buttbot"])
stat_module = ButtStatistics(db["statistics"])
comms_instance = discord_comms.DiscordComms()
shitpost = wordreplacer.WordReplacer(stat_module, phrase_weights, test_environment, nlp)
timer_instance = butt_timeout.Timeout()
vacuum_instance = vacuum.VacuumManager()

guild_configs = butt_config.Config()


async def create_http_session():
    session = aiohttp.ClientSession()
    return session
