import discord
from discord.ext import commands
from discord import app_commands
from Menu_Extras import DropdownView
from Databases.databases import load_data
cursor, cursor2, _, _, _, _ = load_data()

class MenuCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="menu", description="Displays a list of balls")
    @app_commands.describe(user="The user whose balls you want to view")
    @app_commands.describe(reverse="Reverse the order of the list")
    @app_commands.describe(ball="A list with only a specified ball")
    @app_commands.describe(sort="How the list is sorted")
    async def menu(self, interaction: discord.Interaction, user: discord.User = None, reverse: bool = False, ball: str = None, sort: str = None):
        if ball != None and not ball in [x[0] for x in cursor2.execute('SELECT * FROM ball_data').fetchall()]:
            await interaction.response.send_message("The Testball Could Not Be Found", ephemeral = True)
        else:
            if user is None:
                user = interaction.user
            
            if not cursor.execute('SELECT * FROM catches WHERE user_id = ?', (user.id,)).fetchone():
                if user.id == interaction.user.id:
                    await interaction.response.send_message("You don't have any testballs yet!")
                else:
                    await interaction.response.send_message(f"{user.name} doesn't have any testballs yet!")
            elif ball != None and not cursor.execute('SELECT * FROM catches WHERE user_id = ? AND catch_name = ?', (user.id, ball)).fetchone():
                if user.id == interaction.user.id:
                    await interaction.response.send_message(f"You don't have any {ball.replace("_", " ")}s yet!")
                else:
                    await interaction.response.send_message(f"{user.name} doesn't have any {ball.replace("_", " ")}s yet!")
        
            else:    
                allballs = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (user.id,)).fetchall()
                allballs = sorted(allballs, key = lambda x: (-x[6], x[2]))
                
                if ball:
                    allballs = [x for x in allballs if x[1] == ball]

                def ball_data(x):
                    return cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()

                def atk(x):
                    return int(int(ball_data(x)[2]) * (int(x[3]) / 100 + 1 ))

                def hp(x):
                    return int(int(ball_data(x)[3]) * (int(x[4]) / 100 + 1 ))

                def countballs(z):
                    return len([x for x in allballs if x[1] == z])

                if sort == "alphabetic":
                    allballs = sorted(allballs, key = lambda x: x[1])
                elif sort == "catch_date":
                    allballs = sorted(allballs, key = lambda x: x[5])[::-1]
                elif sort == "rarity":
                    allballs = sorted(allballs, key = lambda x: (ball_data(x)[6], x[1]))
                elif sort == "health":
                    allballs = sorted(allballs, key = lambda x: hp(x), reverse = True)
                elif sort == "attack":
                    allballs = sorted(allballs, key = lambda x: atk(x), reverse = True)
                elif sort == "health_bonus":
                    allballs = sorted(allballs, key = lambda x: int(x[4]), reverse = True)
                elif sort == "attack_bonus":
                    allballs = sorted(allballs, key = lambda x: int(x[3]), reverse = True)
                elif sort == "stats_bonus":
                    allballs = sorted(allballs, key = lambda x: sum([int(z) for z in [x[3], x[4]]]), reverse = True)
                elif sort == "total_stats":
                    allballs = sorted(allballs, key = lambda x: atk(x) + hp(x), reverse = True)
                elif sort == "duplicates":
                    allballs = sorted(allballs, key = lambda x: (countballs(x[1]), x[1]), reverse = True)   

                if reverse:
                    allballs = allballs[::-1]

                view = DropdownView(allballs, 1, interaction.user.id)
                await interaction.response.send_message("Choose an option:", view=view)
                view.message = await interaction.original_response() 

    @menu.autocomplete("ball")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        ball_options = [x[0] for x in cursor2.execute('SELECT * FROM ball_data').fetchall()]
        suggestions = [ball for ball in ball_options if current.lower() in ball.lower()]
        return [
            app_commands.Choice(name=suggestion.replace("_", " "), value=suggestion) for suggestion in suggestions
        ]
    
    @menu.autocomplete("sort")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        sort_options = [
            "alphabetic",
            "catch_date",
            "rarity",
            "health",
            "attack",
            "health_bonus",
            "attack_bonus",
            "stats_bonus",
            "total_stats",
            "duplicates"
        ]
        sorts = [sort for sort in sort_options if current.lower() in sort.lower()]
        return [
            app_commands.Choice(name=x, value=x) for x in sorts
        ]

async def setup(bot):
    if bot.tree.get_command("menu"):
        bot.tree.remove_command("menu")
    await bot.add_cog(MenuCommand(bot))