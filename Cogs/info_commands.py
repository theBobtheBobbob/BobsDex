import discord
from discord.ext import commands
from discord import app_commands
import datetime
import time
from Menu_Extras import create_card
from Databases.databases import load_data
cursor, cursor2, _, _, _, _ = load_data()

class InfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Info on a specific ball")
    @app_commands.describe(ball="The ball")
    async def info(self, interaction: discord.Interaction, ball: str):
        ball = "".join([s.replace("🤍", "") for s in ball])
        ball = ball.split()
        
        if not cursor.execute('SELECT * FROM catches WHERE user_id = ? AND catch_name = ? AND catch_id = ?', (interaction.user.id, ball[1], ball[0][1:])).fetchone():
            await interaction.response.send_message("The Testball Could Not Be Found", ephemeral = True)
        else:
            choice = cursor.execute('SELECT * FROM catches WHERE user_id = ? AND catch_name = ? AND catch_id = ?', (interaction.user.id, ball[1], ball[0][1:])).fetchone()
            time_convert = "".join(x if x not in ["-", ":"] else " " for x in choice[5]).split()
            dt = datetime.datetime(int(time_convert[0]), int(time_convert[1]), int(time_convert[2]), int(time_convert[3]), int(time_convert[4]))
            timestamp = int(time.mktime(dt.timetuple()))
            content = "\n".join([
                f"ID:`#{choice[2]}`",
                f"Caught on <t:{timestamp}:f> (<t:{timestamp}:R>)",
                f"Obtained by trade with user {interaction.guild.get_member(int(choice[7])) if interaction.guild.get_member(int(choice[7])) != None else f"with ID {choice[7]}"}\n " if choice[7] != None else " ",
                f"ATK: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[2]) *  (int(choice[3]) / 100 + 1 ))}" + \
                f" ({("+" if choice[3][0] != "-" else "") + str(int(choice[3]))}%)",
                f"HP: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[3]) *  (int(choice[4]) / 100 + 1 ))}" + \
                f" ({("+" if choice[4][0] != "-" else "") + str(int(choice[4]))}%)",
            ])
            
            await interaction.response.send_message(content=content, file=discord.File(fp=create_card(int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[2]) *  (int(choice[3]) / 100 + 1 )),
            int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[3]) *  (int(choice[4]) / 100 + 1 )), choice[1],
            cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[4],
            cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (choice[1],)).fetchone()[5]), filename="card.png"))

                
    @info.autocomplete("ball")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        ball_options = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (interaction.user.id,)).fetchall()
        suggestions = [f"{"🤍" if ball[6] == 1 else ""}#{ball[2]} {ball[1]} ATK:{("+" if int(ball[3]) >= 0 else "") + ball[3]}% HP:{("+" if int(ball[4]) >= 0 else "") + ball[4]}%" for ball in ball_options]
        filtered_suggestions = [s for s in suggestions if current.lower() in s.lower()][:25]
        return [
            app_commands.Choice(name=suggestion.replace("_", " "), value=suggestion) for suggestion in filtered_suggestions
        ]

async def setup(bot):
    if bot.tree.get_command("info"):
        bot.tree.remove_command("info")
    await bot.add_cog(InfoCommand(bot))