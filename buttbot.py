import random
import logging

from phraseweights import PhraseWeights
import butt_library
from config import command_prefix
from discord.ext import tasks

from butt_library import allowed_in_channel, allowed_in_channel_direct
from discord import Message

from shared import guild_configs, test_environment, shitpost, comms_instance, \
    timer_instance as timer_module, bot

log = logging.getLogger('bot.' + __name__)
phrase_weights = PhraseWeights()


class ButtBot:
    def __init__(self):
        self.discordBot = bot

    @staticmethod
    async def docomms(message, channel, guild_id, bypass_for_test=False):
        """sends a message to a provided discord channel in guild."""
        if allowed_in_channel_direct(guild_id, channel.id) or bypass_for_test is True:
            msg = await comms_instance.do_send_message(channel, message)
            return msg  # returns the message obje ct of the message that was sent to discord

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
        log.debug("CHAT_DISPATCH  - GUID %d -  %s " % (
            message.guild.id, message.content))
        try:
            if str(message.content)[0] == command_prefix:
                # command from inside of MC or other game server
                log.debug(
                    "CHAT_DISPATCH  - GUID %d - message is command from game server: %s " % (
                        message.guild.id, message.content))
                await self._process_command_interception(message)
                return
        except IndexError:
            # not in here, skip it and keep going
            pass

        if butt_library.is_word_in_text("rip", message.content):
            log.debug("CHAT_DISPATCH - GUID %d - message is rip from player: %s " % (message.guild.id, message.content))
            await self._process_rip_message(message)

        elif butt_library.is_word_in_text("F", message.content):
            log.debug("CHAT_DISPATCH - GUID %d - message is F from player" % message.guild.id)
            await self._process_f_message(message)

        elif butt_library.is_word_in_text('butt', message.content) is True or butt_library.is_word_in_text('butts',
                                                                                                           message.content) is True:
            log.debug("CHAT_DISPATCH - GUID %d - message contains butt and is going to RSP %s " % (
                message.guild.id, message.content))
            await self._process_butt_message(message)

        else:
            log.debug("CHAT_DISPATCH - GUID %d - message is going to all_other_messages: %s" % (
                message.guild.id, message.content))
            await self._process_all_other_messages(message)

    @staticmethod
    async def _process_command_interception(message: Message):
        """process a command relayed by a bot from in-game."""
        # is this genius? is this not? time will tell.
        try:
            # player, command = message.content.split(command_prefix, 1)
            # remove <> denoting message came from player
            # player = player[1:-2]
            player = message.author.name
            command = message.content.split(command_prefix, 1)[1]
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
                    await self.docomms('kiss my butt F under cooldown', message.channel, message.guild.id)

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

    async def _process_all_other_messages(self, message):
        # here's where im going to evaluate all other sentences for shitposting
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
                                                  guild_configs[message.guild.id].shitpost_freq, commit=False):
                        # passed timer check
                        # try:
                        try:
                            shitpost.perform_text_to_butt(message)

                            if shitpost.butted_sentence:
                                # passes butt check
                                msg = await self.docomms(shitpost.butted_sentence, message.channel,
                                                         message.guild.id)
                                shitpost.buttstatementobject.store(shitpost.butted_sentence, msg.channel.id,
                                                                   msg.id)
                                timer_module.commit_timeout(str(message.guild.id) + 'shitpost',
                                                            guild_configs[message.guild.id].shitpost_freq)
                                shitpost.log_debug_message()
                        except AttributeError:
                            # no butted sentence
                            pass

                else:
                    log.debug("Message2Butt_Processor - sentence over character length.")
        else:
            log.debug("not allowed to speak in channel")
            if test_environment:
                # send to shitpost module for testing.
                # we don't want to talk at all except in my test channel
                shitpost.do_butting_raw_sentence(message)
                print(shitpost.original_sentence)
                print(shitpost.buttstatementobject.get_good_chunks())
                # shitpost.print_debug_message()
                # shitpost.log_disposition()
                if message.channel.id == 435348744016494592:
                    # blow this one up
                    if shitpost.butted_sentence:
                        msg = await self.docomms(shitpost.butted_sentence, message.channel, message.guild.id,
                                                 True)
                        shitpost.buttstatementobject.store(shitpost.butted_sentence, msg.channel.id,
                                                           msg.id)
