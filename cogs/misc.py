import pathlib
from discord import File, app_commands, Interaction
from typing import Optional, List
import os
import random
from discord.ext import commands
from discord import Interaction

from project import PROJECT_PATH

# TODO: stop sending images and just send links lmao

class Misc(commands.Cog):
    def __init__(self, bot : commands.bot):
        self.bot = bot
        self.godroll_dir = PROJECT_PATH / "media/god_roll"
    
    async def godroll_autocomplete(
        self,
        interaction: Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        options = [x.relative_to(self.godroll_dir).name for x in self.godroll_dir.glob('*') if x.is_dir()][1:]

        return [
            app_commands.Choice(name=subdir, value=subdir)
            for subdir in options[:25] if current.lower() in subdir.lower()
        ]

    @commands.hybrid_command()
    async def isopod(self, ctx : commands.Context):
        """real isopod hours"""
        await ctx.reply("https://www.youtube.com/watch?v=3eGJoXs2VtM", mention_author=False)

    @commands.hybrid_command()
    async def opera(self, ctx : commands.Context):
        """"Haaah ha ha ha! I am the star of this play, and it shall be known the world over as a masterpiece!"""
        await ctx.reply("https://media.discordapp.net/attachments/957078513603710976/1347638736858517534/makesweet-q12te0.gif", mention_author=False)

    @commands.hybrid_command(name="godroll")
    @app_commands.autocomplete(subdir=godroll_autocomplete)
    async def send_god_roll_gif(self, ctx : commands.Context, subdir : Optional[str]):
        path = random_image(self.godroll_dir, subdir)

        if path:
            image = File(path)   
            await ctx.reply(file=image, mention_author = False)
        else:
            await ctx.reply("NO GOD ROLL FOR YOU", mention_author = False)

def random_image(dir : pathlib.Path, subdir = None):
    search_dir = dir
    if search_dir.joinpath(subdir).exists():
        search_dir = search_dir / subdir

    return random.choice([x for x in search_dir.glob('**') if x.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif')])

async def setup(bot : commands.Bot):
    await bot.add_cog(Misc(bot))