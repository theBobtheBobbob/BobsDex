import discord
from Databases.databases import load_data
from discord.ui import Modal, TextInput

_, cursor2, _, _, _, _ = load_data()

def paginate(allballs, page=1):
    start_index = (page - 1) * 15
    end_index = page * 15
    return allballs[start_index:end_index]


class PageModal(Modal):
    def __init__(self, allballs, view):
        super().__init__(title="Go To Page")
        self.allballs = allballs
        self.view = view
        self.name_input = TextInput(label="Page", placeholder=f"Enter A Number Between 1 and {(len(self.allballs)+14)//15}")
        self.add_item(self.name_input)
    async def on_submit(self, interaction: discord.Interaction):
        try:
            if int(self.name_input.value) > 0 and int(self.name_input.value) <= (len(self.allballs)+14)//15:
                new_page = int(self.name_input.value)
                if new_page == 1:
                    self.view.children[1].disabled = True
                    self.view.children[3].disabled = False
                elif new_page == (len(self.allballs) + 14)//15:
                    self.view.children[3].disabled = True
                    self.view.children[1].disabled = False
                else:
                    self.view.children[3].disabled = False
                    self.view.children[1].disabled = False  
                self.view.children[2].label = new_page
                self.view.children[1].label = new_page - 1 if new_page - 1 > 0 else "..."
                self.view.children[3].label = new_page + 1 if new_page + 1 <= (len(self.allballs) + 14)//15 else "..."
                
                paginated_balls = paginate(self.allballs, new_page)
                self.view.children[7].options = [
                    discord.SelectOption(
                        label=f"{"❤️" if x[6] == 1 else ""}#{x[2]} {x[1].replace("_", " ")}",
                        description=f"ATK: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[2]) * (int(x[3]) / 100 + 1 ))} " \
                                    f"({'+' if x[3][0] != '-' else ''}{str(int(x[3]))}%)∙" \
                                    f"HP: {int(int(cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[3]) * (int(x[4]) / 100 + 1 ))} " \
                                    f"({'+' if x[4][0] != '-' else ''}{str(int(x[4]))}%)" \
                                    f"{''.join('/' if z == '-' else ' | ' if z == ' ' else z for z in x[5])}",
                        emoji=cursor2.execute('SELECT * FROM ball_data WHERE ball_name = ?', (x[1],)).fetchone()[1]
                    )
                    for x in paginated_balls
                ]
                await interaction.response.edit_message(view=self.view)

            else:
                await interaction.response.send_message(f"Expected A Number Between 1 and {(len(self.allballs)+14)//15}", ephemeral=True)
        except:
            await interaction.response.send_message(fr"Expected A Number Not '{self.name_input.value}'", ephemeral=True)
        

class CustomPageButton(discord.ui.Button):
    def __init__(self, allballs, author):
        super().__init__(label="Skip To Page...", style=discord.ButtonStyle.secondary)
        self.allballs = allballs
        self.author = author
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author:
            await interaction.response.send_message("This Page Cannot Be Controlled By You, Sorry!", ephemeral=True)
        else:
            modal = PageModal(self.allballs, self.view)
            await interaction.response.send_modal(modal)