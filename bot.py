import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is now online!")
    print(f"📊 Connected to {len(bot.guilds)} server(s)")
    print("=" * 40)

async def load_cogs():
    cogs = ["core", "economy", "quests", "shop"]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog {cog}: {e}")

async def main():
    async with bot:
        await load_cogs()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ ERROR: DISCORD_TOKEN environment variable not set!")
            print("Please add your Discord bot token to the Secrets.")
            return
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
