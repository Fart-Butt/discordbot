import asyncio
import spacy
from shutil import copyfile

from discord.ext.commands import Bot

import butt_library
from butt_statistics import ButtStatistics
from buttbot import ButtBot
from config import *
from phraseweights import PhraseWeights

weights = PhraseWeights(discordbot_db, db_secrets[0], db_secrets[1], test_environment)
stat_module = ButtStatistics(stat_db, db_secrets[0], db_secrets[1], test_environment)

client = Bot(description="a bot for farts", command_prefix="", pm_help=False)

channel_configs = butt_library.load_all_config_files()  # global that will hold channel IDs that have configs
command_channels = {}
nlp_ = spacy.load('en_core_web_lg')

if test_environment:
    command_channels[408168696834424832] = ButtBot(client, "development.ini", db_, db_secrets[0], db_secrets[1],
                                                   stat_module, weights, True, nlp_)
    command_channels[199981748098957312] = ButtBot(client, "DPT_document.ini", db_, db_secrets[0], db_secrets[1],
                                                   stat_module, weights, True, nlp_)
    command_channels[154337182717444096] = ButtBot(client, "development.ini", db_, db_secrets[0], db_secrets[1],
                                                   stat_module, weights, True, nlp_)
else:
    for i in channel_configs:
        command_channels[int(i.split("/")[1][:-4])] = ButtBot(client, i, db_, db_secrets[0], db_secrets[1],
                                                              stat_module,
                                                              weights, False, nlp_)
        print("started on guild GUID %s" % i.split("/")[1][:-4])


@client.event
async def on_ready():
    print('Use this link to invite {}:'.format(client.user.name))
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('You are running FartBot V6.0.00')
    print('Created by Poop Poop')
    print('--------')



@client.event
async def on_server_join(server):
    print("joined a server: %s " % server.name)
    if server.id not in command_channels:
        await command_channels[408168696834424832].do_info_log(
            "discordbot:on_join:Joined server %s (%s). Server ID is not found, creating/loading config" %
            (server.name, str(server.id)))
        # copy the config template
        copyfile("config/_config_template", "config/%s.ini" % str(server.id))
        # load it
        await asyncio.sleep(1)
        command_channels[server.id] = ButtBot(client, "config/%s.ini" % server.id, db_,
                                              db_secrets[0], db_secrets[1], stat_module,
                                              weights, False)
    else:
        await command_channels[408168696834424832].do_info_log(
            "discordbot:on_join: Joined server %s (%s). Server config already exists." %
            (server.name, str(server.id)))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author == "BroBot#4514":
        # we dont give a shit about anything this bot says, ever.
        return

    try:
        if str(message.content)[:1] == "&" or str(message.content).partition(" ")[2][0] == "&":
            # command sent from inside of mc server
            send_to_butt_instance = command_channels[message.guild.id].command_dispatch
            await send_to_butt_instance(message)
            return  # dont pass to chat dispatcher
    except IndexError:
        # this message was sent from a regular discord client
        if str(message.content)[:1] == "&":
            send_to_butt_instance = command_channels[message.guild.id].command_dispatch
            await send_to_butt_instance(message)
            return
    except KeyError:
        # command sent from a channel that we dont have a bot loaded for
        pass

    try:
        send_to_butt_instance = command_channels[message.guild.id].chat_dispatch
        await send_to_butt_instance(message)
    except KeyError:
        # command sent from a channel that we dont have a bot loaded for
        pass


async def send_stats_to_db():
    await client.wait_until_ready()
    await asyncio.sleep(5)
    while not client.is_closed:
        stat_module.send_stats_to_db()
        await asyncio.sleep(300)


async def serialize_weights():
    await client.wait_until_ready()
    await asyncio.sleep(5)
    while not client.is_closed:
        if test_environment:
            await asyncio.sleep(10)
        else:
            await asyncio.sleep(300)


client.loop.create_task(send_stats_to_db())
client.loop.create_task(serialize_weights())
client.run(secretkey)