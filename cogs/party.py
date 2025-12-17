import discord
from discord.ext import commands

from database_bot import DatabaseBot
from util.utils import load_json
from sheets.load_party_info import PartyData

display = load_json("en.json")

class Party(commands.Cog):
    def __init__(self, bot : DatabaseBot):
        self.bot = bot
        self.database = self.bot.database

    @commands.command()
    async def partyinfo(self, ctx : commands.Context):
        data = self.database.get_party_info()
        colour = discord.Colour.from_str(data["COLOR"]) if data["COLOR"] else discord.Colour.random()

        var_embed = discord.Embed(
            title=display["party_name"].format(
                party_name=data["NAME"]
            ), 
            colour=colour
        )

        rank = make_bar(
            int(data["RANK"]), 
            int(data["MAX_RANK"]), 
            data["FILLED_RANK"],
            data["UNFILLED_RANK"],
            True
        )
        
        level = display["party_level"].format(
            party_level = data["LEVEL"],
            party_rank = rank
        )

        info = "\n".join(
            [
                display["party_exp"].format(exp=data["TOTAL_EXP"]),
                display["party_hp"].format(hp=data["BASE_HP"]),
                display["party_stats"].format(stats=data["BASE_STATS"]),
                display["party_lunacy"].format(lunacy=data["LUNACY"])
            ]
        )
        
        var_embed.add_field(name=level, value=info, inline=False)
        
        await ctx.send(embed=var_embed)

def make_bar(value : int, max : int, filled : str, unfilled : str, spaced = True):
    bar = ""
    i = 0
    while (i < max):
        bar += filled if i < value else unfilled
        
        if spaced and i < max-1:
            bar += " "

        i += 1
    
    return bar

async def setup(bot : commands.Bot):
    await bot.add_cog(Party(bot))