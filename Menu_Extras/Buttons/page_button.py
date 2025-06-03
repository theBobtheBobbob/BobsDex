import discord
from Databases.databases import load_data
_, cursor2, _, _, _, _ = load_data()

def paginate(allballs, page=1):
    start_index = (page - 1) * 15
    end_index = page * 15
    return allballs[start_index:end_index]

class PageButton(discord.ui.Button):
    def __init__(self, label, page, author, allballs, disabled=False, style=discord.ButtonStyle.secondary):
        super().__init__(label=label, style=style, disabled=disabled)
        self.page = page
        self.allballs = allballs
        self.author = author
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author:
            await interaction.response.send_message("This Page Cannot Be Controlled By You, Sorry!", ephemeral=True)
        else:
            await interaction.response.defer()
            
            current_page = self.view.page
            
            if self.page == "next":
                new_page = current_page + 1
            elif self.page == "previous":
                new_page = current_page - 1
            elif self.page == "<<":
                new_page = 1
            elif self.page == ">>":
                new_page = (len(self.allballs) + 14) // 15
                
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
            
            self.view.page = new_page

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
            await interaction.edit_original_response(view=self.view)
