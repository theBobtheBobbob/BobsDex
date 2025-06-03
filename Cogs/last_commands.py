import discord
from discord.ext import commands
from discord import app_commands
import datetime
import time
from Menu_Extras import create_card
from Databases.databases import load_data
cursor, cursor2, _, _, _, _ = load_data()

class LastCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="last", description="Shows the last caught ball")
    @app_commands.describe(user="The user whose balls you want to view")
    async def last(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user
        if not cursor.execute('SELECT * FROM catches WHERE user_id = ?', (user.id,)).fetchone():
            if user.id == interaction.user.id:
                await interaction.response.send_message("You don't have any testballs yet!")
            else:
                await interaction.response.send_message(f"{user.name} doesn't have any testballs yet!")      
        else:    
            allballs = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (user.id,)).fetchall()
            choice = sorted(allballs, key = lambda x: (x[5]))[-1]
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



async def setup(bot):
    if bot.tree.get_command("last"):
        bot.tree.remove_command("last")
    await bot.add_cog(LastCommand(bot))