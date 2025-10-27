import aiosqlite
import discord
import json
from discord.ext import commands

DB_PATH = "database.db"

async def setup_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                gold INTEGER DEFAULT 0,
                path TEXT,
                inventory TEXT DEFAULT '{}',
                last_mission INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                user_id INTEGER PRIMARY KEY,
                mission_name TEXT,
                xp_reward INTEGER,
                gold_reward INTEGER,
                completed INTEGER DEFAULT 0,
                solo INTEGER
            )
        """)
        await db.commit()
        # Additional tables can be created here

async def get_player(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_player(user_id, **fields):
    query = "UPDATE players SET " + ", ".join(f"{k} = ?" for k in fields.keys()) + " WHERE user_id = ?"
    values = list(fields.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(query, values)
        await db.commit()

def xp_for_next_level(level):
    return 100 * level

def create_profile_embed(user):
    name, level, xp, gold, path = user[1], user[2], user[3], user[4], user[5]
    required = xp_for_next_level(level)
    embed = discord.Embed(title=f"{name}'s Profile", color=discord.Color.purple())
    embed.add_field(name="Path", value=path or "Unchosen", inline=False)
    embed.add_field(name="Level", value=level)
    embed.add_field(name="XP", value=f"{xp}/{required}")
    embed.add_field(name="Gold", value=gold)
    return embed
async def reborn_player(user_id, name, path):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO players (user_id, name, path)
            VALUES (?, ?, ?)
        """, (user_id, name, path))
        await db.commit()

@commands.command()
async def buy(self, ctx, *, item_name):
    user = await get_player(ctx.author.id)
    print("DEBUG user:", user)  # check user data
    if not user:
        await ctx.send("You need to be reborn first! Use `!reborn`.")
        return