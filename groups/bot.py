import discord
from discord import app_commands
import logging
from discord.ext.commands import Bot, Cog, Context, command, has_permissions, is_owner
from butt_library import valid_user_or_bot, can_speak_in_channel
import shared


class ButtbotCommands(app_commands.Group):

    @app_commands.guild_only()
    @app_commands.describe(target='Buttbot')
    async def buttbot(self, interaction: discord.Interaction, target: discord.Member | discord.Role):
        print("test")
        print(target)
        print(interaction)
