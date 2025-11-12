import os
import discord
from discord.ext import commands, tasks
from util.utils import load_json, timestamp_print, print_loaded_commands
import asyncio
import schedule
import time
import atexit
from util.database_manager import FukujinDatabaseManager

config = load_json("config.json")
token = load_json("token.json")["token"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents, owner_id=403778633086271489)
bot.database = FukujinDatabaseManager()

@bot.event
async def on_ready():
    timestamp_print(f"Logged in as {bot.user}; prefix is '{config['prefix']}'")
    print_loaded_commands(bot)

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                timestamp_print(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                timestamp_print(f"Failed to load cog {filename[:-3]}: {e}")

async def main():
    timestamp_print("Starting bot...")
    async with bot:
        await load_cogs()
        await bot.start(token)

try:
    asyncio.run(main()) # i'm gonna live
except KeyboardInterrupt:
    timestamp_print("Shutting down the script due to KeyboardInterrupt!")
    timestamp_print("Attempting final update before exiting...")
    bot.database.push_updates()