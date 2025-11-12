import discord
from discord.ext import commands

from util.load_json import load
import sheets.load_party_info

config = load("config.json")
display = load("en.json")

class Party(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.party = sheets.load_party_info.PartyData(
            config['spreadsheet_id'], 
            config['party_data_sheet_name'], 
            config['party_data_sheet_range']
        )

    @commands.command()
    async def partyinfo(self, ctx):
        try:
            data = self.party.get_party_info()
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
        except Exception as e:
            print(e)
            
    async def refresh(self):
        self.party.load_party_data()

def make_bar(value : int, max : int, filled : str, unfilled : str, spaced : bool):
    bar = ""
    i = 0
    while (i < max):
        bar += filled if i < value else unfilled
        
        if spaced and i < max-1:
            bar += " "

        i += 1
    
    return bar

async def send_error(ctx, header, message):
    await ctx.send(f"**ERROR**: {header}\n{message}")

async def setup(bot):
    await bot.add_cog(Party(bot))