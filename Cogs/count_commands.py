import discord
from discord.ext import commands
from discord import app_commands
from Databases.databases import load_data
cursor, cursor2, _, _, _, _ = load_data()

class CountCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="count", description="Counts how many ball currently owned")
    @app_commands.describe(user="The user whose balls you want to view")
    @app_commands.describe(ball="The specific ball you want")
    async def count(self, interaction: discord.Interaction, user: discord.User = None, ball: str = None):
        if ball != None and not ball in [x[0] for x in cursor2.execute('SELECT * FROM ball_data').fetchall()]:
            await interaction.response.send_message("The Testball Could Not Be Found", ephemeral = True)
        else:
            if user is None:
                user = interaction.user
            allballs = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (user.id,)).fetchall()
            if user == interaction.user:
                if ball == None:
                    await interaction.response.send_message(content=f"You have {len(allballs)} testball{"s" if len(allballs) != 1 else ""}!")
                else:
                    await interaction.response.send_message(content=f"You have {len([x for x in allballs if x[1] == ball])} {ball} testball{"s" if len([x for x in allballs if x[1] == ball]) != 1 else ""}!")
            else:
                if ball == None:
                    await interaction.response.send_message(content=f"{user.name} has {len(allballs)} testball{"s" if len(allballs) != 1 else ""}!")
                else:
                    await interaction.response.send_message(content=f"{user.name} has {len([x for x in allballs if x[1] == ball])} {ball} testball{"s" if len([x for x in allballs if x[1] == ball]) != 1 else ""}!")


    @count.autocomplete("ball")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        ball_options = [x[0] for x in cursor2.execute('SELECT * FROM ball_data').fetchall()]
        suggestions = [ball for ball in ball_options if current.lower() in ball.lower()]
        return [
            app_commands.Choice(name=suggestion, value=suggestion) for suggestion in suggestions
        ]

async def setup(bot):
    if bot.tree.get_command("count"):
        bot.tree.remove_command("count")
    await bot.add_cog(CountCommand(bot))