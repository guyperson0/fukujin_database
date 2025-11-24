import os
from discord.ext import commands
from util.utils import timestamp_print, print_loaded_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(name='shutdown')
    async def close_bot(self, ctx):
        timestamp_print("Closing the script due to shutdown command!")
        await ctx.reply("POWERING DOWN.", mention_author = False)
        await self.bot.close()
        
    @commands.command(name='sync')
    async def push_updates(self, ctx):
        timestamp_print("Pushing updates from admin command push_updates!")
        self.bot.database.push_updates()
        await ctx.reply("UPDATES HAVE BEEN COMMITTED TO THE DATABASE.")

    @commands.command(name='clear')
    async def abort_updates(self, ctx):
        timestamp_print("Clearing edits from admin command abort_updates!")
        self.bot.database.abort_updates()
        await ctx.reply("UPDATES HAVE BEEN REVERTED.")

    @commands.command(hidden=True)
    async def load(self, ctx, cog_name):
        await self.bot.load_extension(f"cogs.{cog_name}")
        await ctx.reply(f"LOADED `{cog_name}`.", mention_author=False)
        timestamp_print(f"Loaded {cog_name}.")
        print_loaded_commands(self.bot)

    @commands.command(hidden=True)
    async def unload(self, ctx, cog_name):
        await self.bot.unload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"UNLOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Unloaded {cog_name}.")
        print_loaded_commands(self.bot)

    @commands.command(hidden=True)
    async def reload(self, ctx, cog_name):
        await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Reloaded {cog_name}.")
        print_loaded_commands(self.bot)

    @commands.command(hidden=True)
    async def reloadall(self, ctx):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = os.path.splitext(filename)[0]
                timestamp_print(f"Attempting to reload {cog_name}.")
                await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED ALL COGS", mention_author=False)
        print_loaded_commands(self.bot)

async def setup(bot):
    await bot.add_cog(Admin(bot))