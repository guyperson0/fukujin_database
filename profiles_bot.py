import os
import discord
from discord.ext import commands
from util.load_json import load
import asyncio
from util.database_manager import FukujinDatabaseManager

config = load("config.json")
token = load("token.json")["token"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=config["prefix"], intents=intents, owner_id=403778633086271489)
bot.database = FukujinDatabaseManager()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}; prefix is '{config['prefix']}'")
    print(f"Loaded commands: {', '.join([command.name for command in bot.commands])}")

async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename[:-3]}")
            except Exception as e:
                print(f"Failed to load cog {filename[:-3]}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

asyncio.run(main()) # i'm gonna kill myself