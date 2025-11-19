import discord

class Paginator(discord.ui.View):
    
    def __init__(self, pages):
        self.pages = pages
        self.index = 0

        self.add_item(self.left)
        self.add_item(self.right)

    @discord.ui.button(emoji=discord.PartialEmoji("makami:1193845873361305604"))
    def page_left(self, interaction, button):
        interaction.message.reply("fortnite", mention_author = False)

    @discord.ui.button(emoji=discord.PartialEmoji("whatthefuku:1440245213086879764"))
    def page_right(self, interaction, button):
        interaction.message.reply("gaming", mention_author = False)