import logging
from discord.ext.commands import Bot, Cog, Context, has_permissions, group, is_owner
import shared
from butt_library import valid_user_or_bot

log = logging.getLogger('bot.' + __name__)


class BotConfig(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @group(invoke_without_command=True)
    @valid_user_or_bot()
    async def config(self, ctx: Context, *args):
        log.debug("got config command from %s in channel %s. arguments are %s" %
                  (str(ctx.message.author.name), str(ctx.message.channel.name), str(*args)))

    @config.command()
    @has_permissions(administrator=True)
    async def allow(self, ctx: Context):
        shared.guild_configs[ctx.message.guild.id].add_channel_to_allowed_channel_list(ctx.message.channel.id)
        await ctx.send("Buttbot will now talk in this wonderful channel and respond to any message")

    @config.command()
    @has_permissions(administrator=True)
    async def remove(self, ctx: Context):
        await ctx.send("Buttbot will longer reply to messages in this channel")
        shared.guild_configs[ctx.message.guild.id].remove_channel_from_allowed_channel_list(
            ctx.message.channel.id)

    @config.command()
    @has_permissions(administrator=True)
    async def botallow(self, ctx: Context, *args):
        await ctx.send("I will now reply to the bot on this guild")
        shared.guild_configs[ctx.message.guild.id].add_whitelisted_bots(args[0])

    @config.command()
    @has_permissions(administrator=True)
    async def botremove(self, ctx: Context, *args):
        await ctx.send("I will no longer reply to the bot on this guild")
        shared.guild_configs[ctx.message.guild.id].remove_whitelisted_bots(args[0])

    @config.command()
    @is_owner()
    async def reloadconfig(self, ctx: Context, *args):
        try:
            shared.guild_configs[args[0]].reload()
            log.debug("reloading config for guid %s" % args[0])
        except IndexError:
            # guid not provided
            log.debug("reloading config for guid %s" % ctx.message.guild.id)
            shared.guild_configs[ctx.message.guild.id].reload()

    @config.error
    async def config_error(self, error, ctx: Context):
        await ctx.send("You do not have permission to run this command in this channel")
