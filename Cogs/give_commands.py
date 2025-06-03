import discord
from discord.ext import commands
from discord import app_commands
from Databases.databases import load_data
cursor, cursor2, _, conn, _, _ = load_data()

class GiveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="give", description="Gives a ball to another user")
    @app_commands.describe(ball="The ball")
    @app_commands.describe(user="The user you wish to give the ball to")
    async def give(self, interaction: discord.Interaction, ball: str, user: discord.User):
        ball = "".join([s.replace("🤍", "") for s in ball])
        ball = ball.split()
        if not cursor.execute('SELECT * FROM catches WHERE user_id = ? AND catch_name = ? AND catch_id = ?', (interaction.user.id, ball[1], ball[0][1:])).fetchone():
            await interaction.response.send_message("The Testball Could Not Be Found", ephemeral = True)
        elif interaction.user == user:
            await interaction.response.send_message("You cannot give a testball to yourself.")
        else:
            if cursor.execute('SELECT * FROM catches WHERE catch_name = ? AND catch_id = ?', (ball[1], ball[0][1:])).fetchone()[6] == 1:
                view = ConfirmView(self, ball, interaction.user, user)
                await interaction.response.send_message("This ball is marked as a favorite. Are you sure you want to give it?", view=view, ephemeral=True)
                view.message = await interaction.original_response()
            else:
                cursor.execute('UPDATE catches SET past_owner = ?, user_id = ?, favorite = ? WHERE catch_name = ? AND catch_id = ?', (interaction.user.id, user.id, 0, ball[1], ball[0][1:]))
                conn.commit()
                await interaction.response.send_message(f"You just gave the testball{cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (ball[1],)).fetchone()[1]}{ball[0]} {ball[1].replace("_", " ")} (`{ball[2][4:]}/{ball[3][3:]}`) to <@{user.id}>")

                
    @give.autocomplete("ball")
    async def autocomplete_callback(self, interaction: discord.Interaction, current: str):
        ball_options = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (interaction.user.id,)).fetchall()
        suggestions = [f"{"🤍" if ball[6] == 1 else ""}#{ball[2]} {ball[1]} ATK:{("+" if int(ball[3]) >= 0 else "") + ball[3]}% HP:{("+" if int(ball[4]) >= 0 else "") + ball[4]}%" for ball in ball_options]
        filtered_suggestions = [s for s in suggestions if current.lower() in s.lower()][:25]
        return [
            app_commands.Choice(name=suggestion.replace("_", " "), value=suggestion) for suggestion in filtered_suggestions
        ]

class ConfirmView(discord.ui.View):
    def __init__(self, cog, ball, user, target_user):
        super().__init__(timeout=60)
        self.cog = cog
        self.ball = ball
        self.user = user
        self.target_user = target_user

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        cursor.execute('UPDATE catches SET past_owner = ?, user_id = ?, favorite = ? WHERE catch_name = ? AND catch_id = ?', 
                       (self.user.id, self.target_user.id, 0, self.ball[1], self.ball[0][1:]))
        conn.commit()
        await interaction.response.edit_message(content="This action has been confirmed", view=self)
        await interaction.followup.send(content=f"You just gave the testball{cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (self.ball[1],)).fetchone()[1]}{self.ball[0]} {self.ball[1].replace("_", " ")} (`{self.ball[2][4:]}/{self.ball[3][3:]}`) to <@{self.target_user.id}>", view=self)
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(content="The action has been cancelled.", view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


async def setup(bot):
    if bot.tree.get_command("give"):
        bot.tree.remove_command("give")
    await bot.add_cog(GiveCommand(bot))