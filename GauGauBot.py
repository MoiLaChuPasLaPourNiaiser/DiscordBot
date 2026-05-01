import discord
from discord import app_commands

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

@bot.tree.command(name="salut", description="Dit bonjour")
async def salut(interaction: discord.Interaction):
    await interaction.response.send_message("Wasup blud")

bot.run("MTQ5OTU5MzU3Nzg2MzQ0NjU5OA.GMkkiU.bUeO5czau8-fQljeqlvKykca67Ls8wi2sXhG4E")