import os
from discord.ext import commands, tasks
from database_bot import DatabaseBot
from util.utils import timestamp_print

class Admin(commands.Cog):
    def __init__(self, bot : DatabaseBot):
        self.bot = bot
        # self.auto_update_database.start()
    
    async def cog_check(self, ctx : commands.Context):
        owner = await self.bot.is_owner(ctx.author)
        if not owner:
            await ctx.reply("THIS COMMAND IS RESTRICTED TO BOT ADMINISTRATORS.", mention_author=False)

        return owner

    @tasks.loop(minutes=20.0)
    async def auto_update_database(self):
        if self.bot.database.has_edits():
            timestamp_print("Automatically updating database!")
            self.bot.database.push_updates()
    
    @commands.command(name='error')
    async def raise_error(self, ctx : commands.Context):
        ctx.reply("RAISING AN ERROR.", mention_author = False)
        raise Exception("Test exception raised from admin command raise_error")

    @commands.command(name='shutdown')
    async def close_bot(self, ctx : commands.Context):
        timestamp_print("Closing the script due to shutdown command!")
        await ctx.reply("POWERING DOWN.", mention_author = False)
        await self.bot.close()
        
    @commands.command(name='sync')
    async def push_updates(self, ctx : commands.Context):
        timestamp_print("Pushing updates from admin command push_updates!")
        self.bot.database.push_updates()
        await ctx.reply("UPDATES HAVE BEEN COMMITTED TO THE DATABASE.", mention_author = False)

    @commands.command(name='clear')
    async def abort_updates(self, ctx : commands.Context):
        timestamp_print("Clearing edits from admin command abort_updates!")
        self.bot.database.abort_updates()
        await ctx.reply("UPDATES HAVE BEEN REVERTED.", mention_author = False)

    @commands.command(hidden=True)
    async def load(self, ctx : commands.Context, cog_name : str):
        await self.bot.load_extension(f"cogs.{cog_name}")
        await ctx.reply(f"LOADED `{cog_name}`.", mention_author=False)
        timestamp_print(f"Loaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    async def unload(self, ctx : commands.Context, cog_name : str):
        await self.bot.unload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"UNLOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Unloaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    async def reload(self, ctx : commands.Context, cog_name : str):
        await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED `{cog_name}`", mention_author=False)
        timestamp_print(f"Reloaded {cog_name}.")
        self.bot.print_loaded_commands()

    @commands.command(hidden=True)
    async def reloadall(self, ctx : commands.Context):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = os.path.splitext(filename)[0]
                timestamp_print(f"Attempting to reload {cog_name}.")
                await self.bot.reload_extension(f"cogs.{cog_name}")
        await ctx.reply(f"RELOADED ALL COGS", mention_author=False)
        self.bot.print_loaded_commands()

async def setup(bot : commands.Bot):
    await bot.add_cog(Admin(bot))