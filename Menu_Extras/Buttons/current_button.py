import discord
class CurrentButton(discord.ui.Button):
    def __init__(self, label, disabled=True):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, disabled=disabled)