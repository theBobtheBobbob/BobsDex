import discord
from discord.ui import View
from Menu_Extras import Dropdown, QuitButton, PageButton, CurrentButton, CustomPageButton

class DropdownView(View):
    def __init__(self, allballs, page, author_id):
        super().__init__(timeout=180)
        self.allballs = allballs  
        self.page = page
        self.author_id = author_id
        if len(allballs) <= 15:
            self.add_item(Dropdown(allballs, page, self.author_id))
            self.add_item(QuitButton(author=self.author_id))
        else:
            self.add_item(PageButton(label="<<", page="<<", allballs=allballs, author=self.author_id))
            self.add_item(PageButton(label="...", page="previous", allballs=allballs, disabled=True, style=discord.ButtonStyle.primary, author=self.author_id))
            self.add_item(CurrentButton(label="1"))
            self.add_item(PageButton(label="2", page="next", allballs=allballs, style=discord.ButtonStyle.primary, author=self.author_id))
            self.add_item(PageButton(label=">>", page=">>", allballs=allballs, author=self.author_id))
            self.add_item(CustomPageButton(allballs=allballs, author=self.author_id))
            self.add_item(QuitButton(author=self.author_id))
            self.add_item(Dropdown(allballs, page, self.author_id))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except AttributeError:
            pass
