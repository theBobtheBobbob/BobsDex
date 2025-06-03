import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import random
import datetime
from Databases.databases import load_data

cursor, cursor2, cursor3, conn, _, conn3 = load_data()

def rarity(x):
    if x <= 10:
        return "t1"
    elif x <= 25:
        return "t2"
    else:
        return "t3"

class UserInfoModal(Modal):
    def __init__(self, view, button, current):
        super().__init__(title="Catch This Testball!")
        self.button = button
        self.view = view
        self.current = current
        self.name_input = TextInput(label="Name Of This Ball", placeholder="Your Guess")
        self.add_item(self.name_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        global clicked
        name = (self.name_input.value).strip().title()
        if clicked == True:
            await interaction.response.send_message(f"{interaction.user.mention} I was caught already!")
        elif name + ".png" == self.current.replace("_", " "):
            clicked = True
            self.button.disabled = True 
            ballname = name.replace(" ", "_")
            balltime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            ballATK = str(random.randint(-20, 20))
            ballHP = str(random.randint(-20, 20))
            ballstatsuse = "/".join([("+" if x[0] != "-" else "") + x + "%" for x in [ballATK, ballHP]])

            cursor.execute('SELECT COUNT(*) FROM catches WHERE catch_name = ?', (ballname,))
            ballid = str(cursor.fetchone()[0] + 1).zfill(8)

            new_ball = False
            if not cursor3.execute('SELECT * FROM user_data WHERE user_id = ? AND ball_name = ?', (str(interaction.user.id), ballname,)).fetchall():
                cursor3.execute('INSERT INTO user_data (user_id, ball_name) VALUES (?, ?)', (str(interaction.user.id), ballname)) 
                conn3.commit()
                new_ball = True
            
            cursor.execute('INSERT INTO catches (user_id, catch_name, catch_id, catch_atk, catch_hp, catch_time) VALUES (?, ?, ?, ?, ?, ?)', (str(interaction.user.id), ballname, ballid, ballATK, ballHP, balltime))
            conn.commit()
            response = f"{interaction.user.mention} You caught **{name}!** `(#{ballid}, {ballstatsuse})`"
            if new_ball:
                response += "\n \n This is a **new countryball** that has been added to your completion!"
            await interaction.response.send_message(response)
            await interaction.message.edit(view=self.view)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Wrong Name!")

class CatchView(View):
    def __init__(self, button, timeout=5):
        super().__init__(timeout=timeout)
        self.button = button
        self.add_item(button)
        self.message = None

    async def on_timeout(self):
        self.button.disabled = True
        await self.message.edit(view=self)

class SpawnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current = None
    
    @app_commands.command(name="spawn", description="Manually spawns a ball (bob only command)")
    async def spawn(self, interaction: discord.Interaction):
        
        self.current = random.choice([x[0] + ".png" for x in cursor2.execute('SELECT * FROM ball_data WHERE ball_rarity = ?', (rarity(random.randint(0,100)),)).fetchall()])

        global clicked
        clicked = False

        button = Button(label="Click Me!", style=discord.ButtonStyle.primary)
        if interaction.user.id == 757769769242853436:
            async def button_callback(interaction):
                modal = UserInfoModal(view, button, self.current)
                await interaction.response.send_modal(modal)

            button.callback = button_callback
            
            view = CatchView(button, timeout=6005)
            await interaction.response.send_message(
                content="A wild testingball appeared!",
                file=discord.File(fr"C:\Users\Chris\Github\Discord-Bot\Art\Spawn Arts\{self.current}"),
                view=view
            )

            view.message = await interaction.original_response()
        else:
           await interaction.response.send_message(content="Error no permissions")
                                                                                                                                                                                
async def setup(bot):
    if bot.tree.get_command("spawn"):
        bot.tree.remove_command("spawn")
    await bot.add_cog(SpawnCommand(bot))
