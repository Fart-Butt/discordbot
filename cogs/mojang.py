import logging
from discord.ext.commands import Bot, Cog, Context, command, BucketType
from discord.ext import commands
import asyncio
from butt_library import valid_user_or_bot, vacuum_enabled_in_guild, can_speak_in_channel
import mojang

log = logging.getLogger('bot.' + __name__)


class MojangCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    @commands.cooldown(1, 10, BucketType.guild)
    @valid_user_or_bot()
    @can_speak_in_channel()
    # TODO: need "minecraft" setting check
    async def mojang(self, ctx: Context):
        status = mojang.Mojang.mojang_status()
        message = []
        if status[0]:
            message.append(
                "aw fuck, looks like %s %s broke (lol)" % (", ".join(status[0]), "are" if len(status[0]) > 1 else "is"))
        if status[1]:
            if status[0]:
                message.append("also %s could be having problems" % ", ".join(status[1]))
            else:
                message.append("looks like %s could be having problems" % ",".join(status[1]))
        if not status[0] and not status[1]:
            message.append("praise notch, it works")
        for t in message:
            async with ctx.typing():
                await asyncio.sleep(3)
            await ctx.send(t)
