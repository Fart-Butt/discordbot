import logging
import asyncio
from discord.ext.commands import Bot, Cog, Context, command, has_permissions, CheckFailure
from butt_library import valid_user_or_bot

log = logging.getLogger('bot.' + __name__)


class BotCommands(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def test(self, ctx: Context, *args):
        print(ctx)
        print(*args)

    @command()
    @has_permissions(administrator=True)
    @valid_user_or_bot()
    async def leave(self, ctx: Context, *args):
        log.info("leaving server %s commanded by %s" % (ctx.message.guild.name, ctx.message.author.name))
        # await self.bot.leave_server(ctx.message.guild)

    @leave.error
    async def leave_error(self, error, ctx: Context):
        log.info("%s tried do_leave in server %s (%s)" % (
            ctx.message.author.name, ctx.message.guild.name, ctx.message.guild.id))
        await ctx.send('fuck you youre not my real dad')
