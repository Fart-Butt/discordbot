import logging
from discord.ext.commands import Bot, Cog, Context, has_permissions, is_owner
from discord.ext import commands
from butt_library import valid_user_or_bot, can_speak_in_channel
import shared

log = logging.getLogger('bot.' + __name__)


class BotCommands(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx: Context, *args):
        print(ctx)
        print(*args)

    @commands.command()
    @has_permissions(administrator=True)
    @valid_user_or_bot()
    @can_speak_in_channel()
    async def leave(self, ctx: Context):
        log.info("leaving server %s commanded by %s" % (ctx.message.guild.name, ctx.message.author.name))
        # await self.bot.leave_server(ctx.message.guild)

    @leave.error
    async def leave_error(self, error, ctx: Context):
        log.info("%s tried do_leave in server %s (%s)" % (
            ctx.message.author.name, ctx.message.guild.name, ctx.message.guild.id))
        shared.comms_instance.do_security_log("%s tried do_leave in server %s (%s)" % (
            ctx.message.author.name, ctx.message.guild.name, ctx.message.guild.id))
        await ctx.send('fuck you youre not my real dad')

    @commands.command()
    @is_owner()
    async def reloadconfig(self, ctx: Context, *args):
        if args:
            if args == "all":
                # reload all configurations
                for i in shared.guild_configs:
                    i.reload()
            else:
                # reload specific guid
                shared.guild_configs[args].reload()
        else:
            shared.guild_configs[ctx.message.guild.id].reload()

    @reloadconfig.error
    async def reloadconfig_error(self, error, ctx: Context):
        log.info("%s tried reloadconfig in server %s (%s)" % (
            ctx.message.author.name, ctx.message.guild.name, ctx.message.guild.id))
        shared.comms_instance.do_security_log("%s tried reloadconfig in server %s (%s)" % (
            ctx.message.author.name, ctx.message.guild.name, ctx.message.guild.id))
