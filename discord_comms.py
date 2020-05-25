import asyncio
import random as rand
from discord.utils import get
import shared


class DiscordComms:
    def __init__(self):
        pass

    @staticmethod
    async def do_send_message(channel, message):
        # this shit sends the messages to the peeps
        await asyncio.sleep(2)
        async with channel.typing():
            await asyncio.sleep(rand.randint(2, 5))
            msg = await channel.send(message)  # dont remove await from here or this shit will break
            return msg

    @staticmethod
    async def do_react(message, client, emoji, cooldown=None):
        if cooldown:
            await asyncio.sleep(cooldown)
        else:
            await asyncio.sleep(rand.randint(2, 5))
        if emoji[0] == ":":
            # custom emoji for channel. we need to get it
            emoji = get(client.emojis, name=emoji[1:])
        await message.add_reaction(emoji)

    @staticmethod
    async def do_react_no_delay(message, client, emoji):
        if emoji[0] == ":":
            # custom emoji for channel. we need to get it
            emoji = get(client.emojis(), name=emoji[1:])
        await message.add_reaction(emoji)

    async def do_security_log(self, message: str):
        await self.do_send_message(shared.bot.get_channel(505226379487346690), message)

    async def do_info_log(self, message: str):
        await self.do_send_message(shared.bot.get_channel(505226325511110658), message)
