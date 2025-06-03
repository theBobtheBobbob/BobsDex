"""dear future me the bot does not handle having more then one inctance at once. shoudl not be to big an issue"""


import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, Button, View, Select
import random
import os
import datetime
from databases.databases import load_data
from bot_token import bot_token

cursor, cursor2, conn, conn2 = load_data()

files = os.listdir(r"C:\Users\Chris\Downloads\Spawn Arts")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
class UserInfoModal(Modal):
    def __init__(self, view, button):
        super().__init__(title="Catch This Testball!")
        self.button = button
        self.view = view
        self.name_input = TextInput(label="Name Of This Ball", placeholder="Your Guess")
        self.add_item(self.name_input)
    async def on_submit(self, interaction: discord.Interaction):
        name = (self.name_input.value).strip().title()
        global clicked
        if clicked == True:
            await interaction.response.send_message(f"{interaction.user.mention} I was caught already!")
        elif name + ".png" == current:
            self.button.disabled = True 
            ballname = name
            ballstats = f"{str(random.randint(-20, 20))}:{str(random.randint(-20, 20))}"
            balltime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            ballstatsuse = "/".join([("+" if x[0] != "-" else "") + x + "%" for x in ballstats.split(":")])
            cursor.execute('SELECT COUNT(*) FROM catches WHERE catch_name = ?', (name,))
            ballid = str(cursor.fetchone()[0] + 1).zfill(8)
            cursor.execute('INSERT INTO catches (user_id, catch_name, catch_id, catch_stats, catch_time) VALUES (?, ?, ?, ?, ?)', (str(interaction.user.id), ballname, ballid, ballstats, balltime))
            conn.commit()
            await interaction.response.send_message(f"{interaction.user.mention} You caught **{name}!** `(#{ballid}, {ballstatsuse})`")
            await interaction.message.edit(view=self.view)
            clicked = True
        else:
            await interaction.response.send_message(f"{interaction.user.mention} Wrong Name!")
@bot.command()
async def image(ctx):
    global current
    current = random.choice(files)
    button = Button(label="Click Me!", style=discord.ButtonStyle.primary)
    global clicked
    clicked = False
    async def button_callback(interaction):
        modal = UserInfoModal(view, button)
        await interaction.response.send_modal(modal)
    button.callback = button_callback
    view = View()
    view.add_item(button)
    await ctx.send(content="A wild testingball appeared!", file=discord.File(fr"C:\Users\Chris\Downloads\Spawn Arts\{current}"), view=view)

@bot.command()
async def caught(ctx):  
    cursor.execute('SELECT * FROM catches WHERE user_id = ?', (ctx.author.id,))
    user_catches = cursor.fetchall() 
    if user_catches:
        catches_list = "\n".join([f"{catch[1]}, {catch[2]}, {catch[3]}, {catch[4]}" for catch in user_catches])
        await ctx.reply(f"Your catches:\n{catches_list}")
    else:
        await ctx.reply("No catches found for you.")

@bot.command()
async def show_menu(ctx):
    def create_embed():
        embed = discord.Embed(
            title="**#1D21A22 Kyrgyzstan**",
            color=discord.Color.dark_gray()
        )
        embed.add_field(name="ATK", value="29(+18%)", inline=True)
        embed.add_field(name="HP", value="160(-9%)", inline=True)
        embed.set_footer(text=f"{datetime.datetime.now().strftime('%Y/%m/%d | %H:%M')}")
        return embed


    class Dropdown(discord.ui.Select):
        def __init__(self):
            hold = cursor.execute('SELECT * FROM catches WHERE user_id = ?', (ctx.author.id,)).fetchall()
            options = [discord.SelectOption(label=f"#{x[2]} {x[1]}",
            description = f"ATK: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[2]) * (int(x[3].split(':')[0]) / 100 + 1 ))}" \
              f"({'+' if x[3].split(':')[0][0] != '-' else ''}{x[3].split(':')[0]}%)∙" \
              f"HP: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[3]) * (int(x[3].split(':')[1]) / 100 + 1 ))}" \
              f"({'+' if x[3].split(':')[1][0] != '-' else ''}{x[3].split(':')[1]}%)∙" \
              f"{''.join('/' if z == '-' else ' | ' if z == ' ' else z for z in x[4])}",
              emoji=cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[1]) for x in hold]
            super().__init__(placeholder="Make a selection", options=options)
            
        async def callback(self, interaction: discord.Interaction):
            if self.values[0] == "Show Stats":
                embed = create_embed()
                file = discord.File(r"C:\Users\Chris\OneDrive\Documents\Bot Stuff\list_art\pixilart-drawing.png")
                embed.set_thumbnail(url="attachment://image.png")
                await interaction.response.send_message(embed=embed, file=file)

    class DropdownView(View):
        def __init__(self):
            super().__init__()
            self.add_item(Dropdown())

    await ctx.send("Choose an option:", view=DropdownView())


bot.run(bot_token) 