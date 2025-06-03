import discord

class QuitButton(discord.ui.Button):
    def __init__(self, author):
        super().__init__(label="Quit", style=discord.ButtonStyle.danger)
        self.author = author
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author:
            await interaction.response.send_message("This Page Cannot Be Controlled By You, Sorry!", ephemeral=True)
        else:
            await interaction.response.defer()
            for child in self.view.children:
                child.disabled = True
            await interaction.edit_original_response(view=self.view)