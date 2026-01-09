import discord
from typing import Callable, List

class PaginatorButton(discord.ui.Button['Paginator']):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def update(self):
        return

class FirstButton(PaginatorButton):
    def __init__(self):
        super().__init__(emoji='⏮️')
        self.disabled = True
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        
        self.view.index = 0
        await self.view.update(interaction)
        
    def update(self):
        if self.view is None:
            return
        self.disabled = (self.view.index <= 0)

class PreviousButton(PaginatorButton):
    def __init__(self):
        super().__init__(emoji='⬅️')
        self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        if (self.view.index - 1) < 0:
            return
        
        self.view.index -= 1
        await self.view.update(interaction)
        
    def update(self):
        if self.view is None:
            print("???")
            return
        self.disabled = (self.view.index <= 0)

class NextButton(PaginatorButton):
    def __init__(self):
        super().__init__(emoji='➡️')
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        if (self.view.index + 1 >= self.view.page_count):
            return
        
        self.view.index += 1
        await self.view.update(interaction)

    def update(self):
        if self.view is None:
            return
        self.disabled = (self.view.index >= self.view.page_count - 1)

class LastButton(PaginatorButton):
    def __init__(self):
        super().__init__(emoji='⏭️')
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            return
        if self.view.page_count == 0:
            return
       
        self.view.index = self.view.page_count - 1
        await self.view.update(interaction)

    def update(self):
        if self.view is None:
            return
        self.disabled = (self.view.index >= self.view.page_count - 1)

class Paginator(discord.ui.View):
    children: List[PaginatorButton]

    def __init__(self, page_count, get_page: Callable[[int], discord.Embed], *, index = 0, timeout=180.0):
        super().__init__(timeout=timeout)
        self.msg: discord.Message = None
        self.index = index
        self.page_count = page_count
        self.get_page = get_page

        self.add_item(FirstButton())
        self.add_item(PreviousButton())
        self.add_item(NextButton())
        self.add_item(LastButton())

        self.update_children()

    async def update(self, interaction: discord.Interaction):
        self.update_children()
        await interaction.response.edit_message(embed=self.get_page(self.index), view=self)

    def update_children(self):
        for child in self.children:
            child.update()

    async def on_timeout(self):
        if not self.msg:
            return
        
        for child in self.children:
            child.disabled = True
        
        await self.msg.edit(view=self)