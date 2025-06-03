import discord
from discord.ext import commands
from discord import app_commands
from Databases.databases import load_data
cursor, _, _, _, _, _ = load_data()

class CaughtCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="caught", description="An early development command has little to no use")
    async def caught(self, interaction: discord.Interaction):
        cursor.execute('SELECT * FROM catches WHERE user_id = ?', (interaction.user.id,))
        user_catches = cursor.fetchall()
        
        if user_catches:
            catches_list = "\n".join([f"{catch[1]}, {catch[2]}, {catch[3]}, {catch[4]}, {catch[5]}" for catch in user_catches])
            await interaction.response.send_message(f"Your catches:\n{catches_list}")
        else:
            await interaction.response.send_message("No catches found for you.")

async def setup(bot):
    if bot.tree.get_command("caught"):
        bot.tree.remove_command("caught")
    await bot.add_cog(CaughtCommand(bot))