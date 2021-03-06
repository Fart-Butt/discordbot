import asyncio
import random
import time
import logging
from config import command_prefix
import concurrent.futures

import mojang as mj
from butt_library import is_word_in_text, allowed_in_channel, allowed_in_channel_direct
from discord import Message

from shared import guild_configs, test_environment, phrase_weights, shitpost, comms_instance, \
    timer_instance as timer_module, vacuum_instance as vacuum, db, bot

log = logging.getLogger('bot.' + __name__)


class ButtBot:
    def __init__(self):
        self.discordBot = bot
        self.mojang = mj.Mojang()
        self.discordBot.loop.create_task(self.scraper_subscription_task())

    async def scraper_subscription_task(self):
        await self.discordBot.wait_until_ready()
        log.debug("SCRAPER - starting scraper task")
        while not self.discordBot.is_closed():
            await asyncio.sleep(10)
            log.debug("SCRAPER - started")
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                for i in vacuum:
                    executor.map(vacuum[i].playtime_scraper())
            log.debug("SCRAPER - ended")

    def is_played_time_loop_running(self):
        pass
        # if self.config.getboolean('vacuum', 'enabled') is True:
        #    print("")
        #    d = self._played_time_loop_last_ran - datetime.datetime.utcnow()
        #    d = abs(int(d.total_seconds()))
        #    if d > 30:
        #        # has not run in 30 or more seconds
        #        self.do_info_log("I'm a broken piece of shit and had to reboot the background task")
        #        self.discordBot.loop.create_task(self.my_background_task())

    async def butt_message_processing(self):
        await self.discordBot.wait_until_ready()
        while not self.discordBot.is_closed():
            if test_environment:
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(120)
            await self.check_stored_reactions()

    @staticmethod
    async def docomms(message, channel, guild_id, bypass_for_test=False):
        """sends a message to a provided discord channel in guild."""
        if allowed_in_channel_direct(guild_id, channel.id) or bypass_for_test is True:
            msg = await comms_instance.do_send_message(channel, message)
            return msg  # returns the message object of the message that was sent to discord

    async def doreact(self, message, emojis):
        """adds a reaction to a message object."""
        # TODO: stats re-integration
        if allowed_in_channel(message):
            # self.stats.message_store(message.channel.id)
            # self.stats.disposition_store(message.guild.id, message.channel.id,
            #                             "React", emojis, message.content)
            await comms_instance.do_react(message, self.discordBot, emojis)

    async def chat_dispatch(self, message: Message):
        """master chat processing function. determines where to send message for processing (shitposting, reverse
        shitposting, RIP, etc.)"""
        try:
            if str(message.content).partition(" ")[2][0] == command_prefix:
                # command from inside of MC or other game server
                log.debug(
                    "CHAT_DISPATCH  - GUID %d - message is command from game server: %s " % (
                        message.guild.id, message.content))
                await self._process_command_interception(message)
                return
        except IndexError:
            # not in here, skip it and keep going
            pass

        if is_word_in_text("RIP:", message.content):
            log.info("CHAT_DISPATCH - GUID %d - message is death alert from game server: %s " % (
                message.guild.id, message.content))
            await self._process_death_message(message)

        elif is_word_in_text("rip", message.content):
            log.info("CHAT_DISPATCH - GUID %d - message is rip from player: %s " % (message.guild.id, message.content))
            await self._process_rip_message(message)

        elif is_word_in_text("F", message.content):
            log.info("CHAT_DISPATCH - GUID %d - message is F from player" % message.guild.id)
            await self._process_f_message(message)

        elif is_word_in_text('butt', message.content) is True or is_word_in_text('butts', message.content) is True:
            log.info("CHAT_DISPATCH - GUID %d - message contains butt and is going to RSP %s " % (
                message.guild.id, message.content))
            await self._process_butt_message(message)

        else:
            log.info("CHAT_DISPATCH - GUID %d - message is going to all_other_messages: %s" % (
                message.guild.id, message.content))
            await self._process_all_other_messages(message)

    @staticmethod
    async def _process_command_interception(message: Message):
        """process a command relayed by a bot from in-game."""
        # is this genius? is this not? time will tell.
        try:
            player, command = message.content.split(command_prefix, 1)
            # remove <> denoting message came from player
            player = player[1:-2]
        except IndexError:
            log.debug("_PROCESS_COMMAND_INTERCEPTION - no special character found in message.")
            # no command prefix found in message.
            player = ''
            command = ''
        if command:
            # 5/30/20 - added player sending command as argument to the command so it can be used by commands
            # for personalized processing.
            message.content = "%s%s %s" % (command_prefix, command, player)
            # i wanted to use bot.process_commands here but can't since it explictly filters out bots.  The whole point
            # of this command is to process text sent by bots.
            # I make sure that the commands are only processed by allowed bots in a decorator on the commands themselves
            ctx = await bot.get_context(message)
            await bot.invoke(ctx)

    @staticmethod
    async def process_cached_reaction_message(message: Message, noun: str):
        """process emoji reactions from a previously butted sentence."""
        # i know this looks dumb as hell but trust me on this one
        message = await message.channel.fetch_message(message.id)
        if test_environment:
            log.debug("running cached reaction on id %s" % message.id)
        votes = phrase_weights.process_reactions(message.reactions)
        log.debug("votes tallied to %d" % votes)
        phrase_weights.adjust_weight(noun, votes)

    async def check_stored_reactions(self):
        """check recent butted messages and process their reaction emojis."""
        for items in phrase_weights.get_messages():
            check_timer = 300
            if test_environment:
                check_timer = 15
            if time.time() - items[0] > check_timer:
                await self.process_cached_reaction_message(items[1], items[2])
                phrase_weights.remove_message(items[0], items[1], items[2])

    async def _process_rip_message(self, message: Message):
        """process someone saying RIP in channel.
        Permission: default on, can be toggled in table config, row "RIP"
        TODO: add command to turn on or off."""

        log.debug("PROCESS_RIP_MESSAGE - recieved rip")
        if allowed_in_channel(message) and \
                guild_configs[message.guild.id].rip:
            # self.stats.message_store(message.channel.id)
            if timer_module.check_timeout(str(message.channel.id) + 'rip',
                                          guild_configs[message.guild.id].shitpost_freq):
                # self.stats.disposition_store(message.guild.id, message.channel.id,
                #                             "RIP", "RIP")
                if random.randint(1, 20) == 5:
                    await self.docomms('Ya, butts', message.channel, message.guild.id)
                else:
                    await self.docomms('Ya, RIP', message.channel, message.guild.id)
            else:
                pass
                # self.stats.disposition_store(message.guild.id, message.channel.id,
                #                             "RIP cooldown", "RIP cooldown")

    @staticmethod
    async def _process_death_message(message: Message):
        """recieved a notification from the minecraft interface bot that someone died on the server"""
        log.debug("PROCESS_DEATH_MESSAGE - message recieved, %s" % message)
        if (str(message.author) == 'Progress#6064' and message.content[:4] == 'RIP:') or \
                (str(message.author) == '💩💩#4048' and message.content[:4] == 'RIP:'):
            vacuum[message.guild.id].add_death_message(message.content)

    async def _process_f_message(self, message):
        if allowed_in_channel(message) and guild_configs[message.guild.id].f:
            # self.stats.message_store(message.channel.id)
            if timer_module.check_timeout(str(message.channel.id) + 'f',
                                          guild_configs[message.guild.id].shitpost_freq):
                # self.stats.disposition_store(message.guild.id, message.channel.id,
                #                             "F", "F")
                await self.docomms('Ya, F', message.channel, message.guild.id)
            else:
                # self.stats.disposition_store(message.guild.id, message.channel.id,
                #                             "F cooldown", "F cooldown")
                if random.randint(1, 100) == 44:
                    await self.docomms('suck my dick F under cooldown', message.channel, message.guild.id)

    async def _process_butt_message(self, message):
        # TODO: stats module re-integration
        if allowed_in_channel(message):
            # self.stats.message_store(message.channel.id)
            if random.randint(1, 6) == 3:
                if timer_module.check_timeout(str(message.channel.id) + 'rsp',
                                              guild_configs[message.guild.id].shitpost_freq):
                    rshitpost = shitpost.rspeval(message.content)
                    if rshitpost:
                        # self.stats.disposition_store(message.guild.id, message.channel.id,
                        #                             "RSP", "RSP", message.content)
                        await self.docomms(rshitpost, message.channel, message.guild.id)
                else:
                    pass
            # self.stats.disposition_store(message.guild.id, message.channel.id,
            #                             "RSP cooldown", "RSP cooldown")
            elif random.randint(1, 3) == 3:
                if timer_module.check_timeout(str(message.channel.id) + 'rsp_emoji',
                                              guild_configs[message.guild.id].shitpost_freq):
                    await self.doreact(message,
                                       random.choice(guild_configs[message.guild.id].emojis))

    async def record_player_guid(self, player):
        players = db["minecraft"].do_query(
            "select count(player_name) as c from progress.minecraft_players where player_name = %s",
            (player,)
        )
        if players[0]['c'] == 0:
            # we dont see this player in the db, let's record the guid
            db["minecraft"].do_insert("insert into progress.minecraft_players "
                                      "(player_name, player_guid)"
                                      "VALUES (%s, %s)",
                                      (player, self.mojang.mojang_user_to_uuid(player)))
        else:
            # we see this player name in the db, no need to record guid
            pass

    async def _process_all_other_messages(self, message):
        # here's where im going to evaluate all other sentences for shitposting
        if is_word_in_text("left the game", message.content) or is_word_in_text("joined the game", message.content):
            player = message.content.split(" ")[0]
            await self.record_player_guid(player)
            # this is a join or part message and we are going to ignore it
            # welcome to progress
            if message.author.id == 249966240787988480 and is_word_in_text("joined the game", message.content):
                hwsp = vacuum[message.guild.id].have_we_seen_player(player)
                if hwsp:
                    log.debug("have not seen player before: %s" % player)
                    await self.docomms(hwsp, message.channel, message.guild.id)

        else:
            if allowed_in_channel(message):
                log.debug("allowed to speak in channel")
                # do not send to shitpost module if we aren't allowed to talk in the channel in question.
                if test_environment:
                    # always reply in test environment
                    rv = [1, 1, 1]
                else:
                    rv = [1, 5, 3]
                if random.randint(rv[0], rv[1]) == rv[2]:
                    # message length check
                    if len(message.content.split()) < guild_configs[message.guild.id].max_sentence_length:
                        if timer_module.check_timeout(str(message.guild.id) + 'shitpost',
                                                      guild_configs[message.guild.id].shitpost_freq):
                            # passed timer check
                            # try:
                            shitpost.perform_text_to_butt(message)

                            if shitpost.successful_butting():
                                # passes butt check
                                msg = await self.docomms(shitpost.butted_sentence, message.channel, message.guild.id)
                                phrase_weights.add_message(message, shitpost.get_noun())
                                shitpost.log_disposition()
                    else:
                        log.debug("Message2Butt_Processor - sentence over character length.")
            else:
                log.debug("not allowed to speak in channel")
                if test_environment:
                    # send to shitpost module for testing.
                    # we don't want to talk at all except in my test channel
                    shitpost.perform_text_to_butt(message)
                    shitpost.print_debug_message()
                    shitpost.log_disposition()
                    if message.channel.id == 435348744016494592:
                        # blow this one up
                        if shitpost.successful_butting():
                            msg = await self.docomms(shitpost.butted_sentence, message.channel, message.guild.id, True)
                            phrase_weights.add_message(msg, shitpost.get_noun())
