import os
from discord import Object
from discord.ext import commands, tasks
from database_bot import DatabaseBot
from util.utils import timestamp_print

class Admin(commands.Cog):
    def __init__(self, bot : DatabaseBot):
        self.bot = bot
        self.auto_update_database.start()

    @tasks.loop(minutes=20.0)
    async def auto_update_database(self):
        if self.bot.database.has_edits():
            timestamp_print("Automatically updating database!")
            self.bot.database.push_updates()
    
    @commands.command(name='error')
    @commands.is_owner()
    async def raise_error(self, ctx : commands.Context):
        ctx.reply("RAISING AN ERROR.", mention_author = False)
        raise Exception("Test exception raised from admin command raise_error")

    @commands.command(name='shutdown')
    @commands.is_owner()
    async def close_bot(self, ctx : commands.Context):
        timestamp_print("Closing the script due to shutdown command!")
        await ctx.reply("POWERING DOWN.", mention_author = False)
        await self.bot.close()
        
    @commands.command(name='push')
    @commands.is_owner()
    async def push_updates(self, ctx : commands.Context):
        timestamp_print("Pushing updates from admin command push_updates!")
        self.bot.database.push_updates()
        await ctx.reply("UPDATES HAVE BEEN COMMITTED TO THE DATABASE.", mention_author = False)

    @commands.command(name='clear', aliases=['abort', 'refresh'])
    @commands.is_owner()
    async def abort_updates(self, ctx : commands.Context):
        timestamp_print("Clearing edits and refreshing from admin command abort_updates!")
        self.bot.database.abort_updates()
        await ctx.reply("REFRESHING DATABASE AND DISCARDING EDITS.", mention_author = False)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx : commands.Context, cog_name : str):
        await self.bot.load_extension(f"cogs.{cog_name}")
        await ctx.reply(f"LOADED `{cog_name}`.", mention_author=False)
        timestamp_print(f"Loaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx : commands.Context, cog_name : str):
        await self.bot.unload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"UNLOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Unloaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx : commands.Context, cog_name : str):
        await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Reloaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reloadall(self, ctx : commands.Context):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = os.path.splitext(filename)[0]
                timestamp_print(f"Attempting to reload {cog_name}.")
                await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED ALL COGS", mention_author=False)
        self.bot.print_loaded_commands()

    @commands.command(hidden=True, name='refreshmembers', aliases=['reloadmembers'])
    @commands.is_owner()
    async def refresh_members(self, ctx : commands.Context):
        self.bot.database.reload_members()
        await ctx.reply(f"MEMBERS RELOADED.", mention_author=False)
        
    @commands.command(hidden=True, name='setdatabase', aliases=['setdb'])
    @commands.is_owner()
    async def set_database(self, ctx : commands.Context, config_name):
        try: 
            self.bot.set_database(config_name)
            await ctx.reply(f"SET DATABASE TO `{config_name}`.", mention_author=False)
        except FileNotFoundError:
            await ctx.reply(f"NO DATABASE `{config_name}` WAS FOUND.", mention_author=False)

    @commands.command(hidden=True, name='globalsync')
    @commands.is_owner()
    async def sync_commands_global(self, ctx: commands.Context):
        synced = await self.bot.tree.sync()
        await ctx.reply(f"SYNCED {(len(synced))} COMMANDS.", mention_author=False)

    @commands.command(hidden=True, name='localsync', aliases=['sync'])
    @commands.is_owner()
    async def sync_commands_local(self, ctx : commands.Context):
        self.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await self.bot.tree.sync(guild=ctx.guild)
        await ctx.reply(f"SYNCED {len(synced)} COMMANDS.", mention_author=False)

    @commands.command(hidden=True, name="globalclear")
    @commands.is_owner()
    async def clear_commands_global(self, ctx: commands.Context):
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync()
        await ctx.reply(f"CLEARED GLOBAL TREE OF COMMANDS.", mention_author=False)

    @commands.command(hidden=True, name="localclear")
    @commands.is_owner()
    async def clear_commands_local(self, ctx: commands.Context):
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.reply(f"CLEARED LOCAL TREE OF COMMANDS.", mention_author=False)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(Admin(bot))