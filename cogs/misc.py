from discord import File, app_commands, Interaction
from typing import Optional, List
import os
import random
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot : commands.bot):
        self.bot = bot
        self.media_dir = "../media"
    
    @commands.hybrid_command()
    async def isopod(self, ctx : commands.Context):
        """real isopod hours"""
        await ctx.reply("https://www.youtube.com/watch?v=3eGJoXs2VtM", mention_author=False)

    @commands.hybrid_command()
    async def opera(self, ctx : commands.Context):
        """"Haaah ha ha ha! I am the star of this play, and it shall be known the world over as a masterpiece!"""
        await ctx.reply("https://media.discordapp.net/attachments/957078513603710976/1347638736858517534/makesweet-q12te0.gif", mention_author=False)

    @commands.hybrid_command(name="godroll")
    async def send_god_roll_gif(self, ctx : commands.Context, subdir : Optional[str]):
        path = random_image(f"{self.media_dir}/god_roll", subdir)

        if path:
            file = File(path)   
            await ctx.reply(file=file, mention_author = False)
        else:
            await ctx.reply("NO GOD ROLL FOR YOU", mention_author = False)

def random_image(dir : str, subdir = None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_dir = os.path.abspath(os.path.join(base_dir, dir))
    
    image_files = []

    if subdir and os.path.exists(os.path.join(search_dir, subdir)):
        search_dir = os.path.join(search_dir, subdir)

    for root, _, files in os.walk(search_dir):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif'):
                image_files.append(os.path.join(root, file))

    if not image_files:
        return None
    
    return random.choice(image_files)

async def setup(bot : commands.Bot):
    await bot.add_cog(Misc(bot))