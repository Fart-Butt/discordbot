import re
from discord.ext.commands import Context, check
import shared
import logging
from rfc3987 import parse

log = logging.getLogger('bot.' + __name__)


def plurality(word, count):
    return word + "s" if (count > 1 or count == 0) else word


def loud_noises(word, count):
    return str(count) + " " + plurality(word, count) if count > 0 else ""


def is_word_in_text(word, text):
    pattern = r'(^|[^\w]){}([^\w]|$)'.format(word)
    pattern = re.compile(pattern, re.IGNORECASE)
    matches = re.search(pattern, text)
    return bool(matches)


def strip_IRI(sentence: str) -> str:
    text = sentence.split(" ")
    for w in text:
        try:
            if parse(w, rule="IRI"):
                text.remove(w)
        except ValueError:
            # we expect this to happen when the text is not an IRI, so we can ignore this
            pass
    return " ".join(text)


def detect_code_block(text):
    words = text.split(" ")
    for w in words:
        if w == "```" or w[:3] == "```" or w[-3:] == "```":
            return True
    return False


def get_indexes(list_, word):
    return [i for (y, i) in zip(list_, range(len(list_))) if word == y]


def _should_i_reply_to_bot(ctx: Context):
    """Checks to see if we should reply to message author.  specific to users discord flags as bots"""
    if ctx.message.author.id in shared.guild_configs[ctx.message.channel.id].allowed_bots:
        # we should always talk to this bot
        log.debug("SHOULD_I_REPLY_TO_USER: bot check passed")
        return True
    else:
        log.debug("SHOULD_I_REPLY_TO_USER: bot check failed - %d - %s" %
                  (ctx.message.guild.id, shared.guild_configs[ctx.message.guild.id].allowed_bots))
        return False


def _should_i_reply_to_user(ctx: Context):
    """Checks to see if we should reply to message author.  specific to non bot users"""
    if ctx.message.author.id not in shared.guild_configs[ctx.message.channel.id].banned_users:
        log.debug("SHOULD_I_REPLY_TO_USER: user check passed")
        return True
    else:
        log.debug(
            "SHOULD_I_REPLY_TO_USER: user check failed - %s" % shared.guild_configs[ctx.message.guild.id].banned_users)
        return False


def should_i_reply_to_user(ctx: Context):
    """master clearinghouse for checking if buttbot should reply to user. checks user block list and accepted bot
    list on a per-guild basis.  also checks global ban list."""
    if ctx.message.author.bot:
        # bot user (flag set by discord server)
        return _should_i_reply_to_bot(ctx)
    return _should_i_reply_to_user(ctx)


def valid_user_or_bot():
    """makes sure user generating context is a valid to talk to"""

    def predicate(ctx: Context):
        return should_i_reply_to_user(ctx)

    return check(predicate)


def vacuum_enabled_in_guild():
    """makes sure vacuum module is enabled in guild config"""

    def predicate(ctx: Context):
        return shared.guild_configs[ctx.message.guild.id].vacuum

    return check(predicate)


def can_speak_in_channel():
    """verifies buttbot is allowed to talk in message channel"""

    def predicate(ctx: Context):
        log.debug("CAN_SPEAK_IN_CHANNEL: %s, %d, %s" %
                  (ctx.message.channel.id in shared.guild_configs[ctx.message.guild.id].allowed_channels,
                   ctx.message.channel.id,
                   shared.guild_configs[ctx.message.guild.id].allowed_channels))
        return ctx.message.channel.id in shared.guild_configs[ctx.message.guild.id].allowed_channels

    return check(predicate)
