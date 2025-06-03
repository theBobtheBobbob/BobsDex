import discord
from discord.ext import commands
from discord import app_commands
from Databases.databases import load_data
cursor, cursor2, _, conn, _, _ = load_data()

class FavoriteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="favorite", description="Adds and removes balls from favorites")
    @app_commands.describe(ball="The ball")
    async def favorite(self, interaction: discord.Interaction,ball: str):
        ball = "".join([s.replace("🤍", "") for s in ball])
       
        ball = ball.split()
        if not cursor.execute('SELECT * FROM catches WHERE user_id = ? AND catch_name = ? AND catch_id = ?', (interaction.user.id, ball[1], ball[0][1:])).fetchone():
            await interaction.response.send_message("The Testball Could Not Be Found", ephemeral = True)
        else:
            if cursor.execute('SELECT * FROM catches WHERE catch_name = ? AND catch_id = ?', (ball[1], ball[0][1:])).fetchone()[6] == 0:
                cursor.execute('UPDATE catches SET favorite = ? WHERE catch_name = ? AND catch_id = ?', (1, ball[1], ball[0][1:]))
                conn.commit()
                await interaction.response.send_message(f"{cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (ball[1],)).fetchone()[1]}`{ball[0]}`{ball[1].replace("_", " ")} is now a favorite testball!", ephemeral = True)
            else:
                cursor.execute('UPDATE catches SET favorite = ? WHERE catch_name = ? AND catch_id = ?', (0, ball[1], ball[0][1:]))
                conn.commit()
                await interaction.response.send_message(f"{cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (ball[1],)).fetchone()[1]}`{ball[0]}`{ball[1].replace("_", " ")} isn't a favorite testball anymore!", ephemeral = True)

    @favorite.autocomplete("ball")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        ball_options = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (interaction.user.id,)).fetchall()
        suggestions = [f"{"🤍" if ball[6] == 1 else ""}#{ball[2]} {ball[1]} ATK:{("+" if int(ball[3]) >= 0 else "") + ball[3]}% HP:{("+" if int(ball[4]) >= 0 else "") + ball[4]}%" for ball in ball_options]
        filtered_suggestions = [s for s in suggestions if current.lower() in s.lower()][:25]
        filtered_suggestions = [s for s in suggestions]
        return [
            app_commands.Choice(name=suggestion.replace("_", " "), value=suggestion) for suggestion in filtered_suggestions
        ]

async def setup(bot):
    if bot.tree.get_command("favorite"):
        bot.tree.remove_command("favorite")
    await bot.add_cog(FavoriteCommand(bot))