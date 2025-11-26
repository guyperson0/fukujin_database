import os
import discord
import asyncio

from util.utils import load_json, timestamp_print
from database_bot import DatabaseBot

config = load_json("config.json")
token = load_json("token.json")["token"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = DatabaseBot(command_prefix=config["prefix"], intents=intents, owner_id=config["owner_id"])

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

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
            timestamp_print("Shutting down the script due to KeyboardInterrupt!")
    finally:
        if not bot.is_closed():
            asyncio.run(bot.close())
    
        timestamp_print("Attempting final update before exiting...")
        bot.database.push_updates()
        timestamp_print("Bot closed; good night, world.")