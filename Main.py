import discord
from discord.ext import commands
from bot_token import bot_token
import os
#dear future me the bot does not handle having more then one inctance at once. should not be to big an issue
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'Cogs.{filename[:-3]}')
            print(f'Loaded extension: {filename[:-3]}')

    await bot.tree.sync() 
    print("Slash commands synced.") 

bot.run(bot_token)