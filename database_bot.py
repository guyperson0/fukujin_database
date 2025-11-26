from discord.ext import commands
import gspread

from util.database_manager import FukujinDatabaseManager
from util.utils import timestamp_print, send_error
from traceback import print_exception

class DatabaseBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gc = gspread.service_account(filename="sheets/credentials/service_account.json")
        self.database = FukujinDatabaseManager(self.gc)

    def print_loaded_commands(self):
        timestamp_print(f"Loaded commands: {', '.join([command.name for command in self.commands])}")
    
    async def on_ready(self):
        timestamp_print(f"Logged in as {self.user}; prefix is '{self.command_prefix}'")
        self.print_loaded_commands()

    async def on_command_error(self, ctx : commands.Context, e : Exception):
        if isinstance(e, commands.errors.CommandNotFound):
            return
        elif isinstance(e, commands.errors.MissingRequiredArgument):
            await send_error(ctx, "MISSING REQUIRED ARGUMENT", "CHECK THE COMMAND SYNTAX WAS PROPERLY FOLLOWED.")
        else:
            await send_error(ctx, "UNKNOWN ERROR", "PLEASE CONTACT THE ADMINISTRATOR AS SOON AS POSSIBLE.")
            timestamp_print(f"{ctx.author.name} ({ctx.author.id}) encountered an error invoking:")
            timestamp_print(f"\t{ctx.message.content}")
            print_exception(e)