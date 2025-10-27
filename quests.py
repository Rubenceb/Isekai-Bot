import discord
from discord.ext import commands
import aiosqlite
import random
import time
from classes import apply_class_bonus

MISSION_COOLDOWN = 3600  # 1 hour
DUEL_COOLDOWN = 1800     # 30 minutes

MISSIONS = [
    {"name": "⚔️ Slay 5 goblins", "xp": 150, "gold": 200, "solo": True},
    {"name": "🪵 Gather 10 herbs", "xp": 120, "gold": 150, "solo": True},
    {"name": "🧭 Explore the Mystic Cave", "xp": 200, "gold": 250, "solo": False},
    {"name": "🏹 Protect a caravan", "xp": 180, "gold": 220, "solo": False},
    {"name": "🐉 Hunt a baby dragon", "xp": 300, "gold": 400, "solo": False}
]

class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- SOLO OR PARTY MISSIONS ----------------
    @commands.command()
    async def missions(self, ctx):
        """Show a random mission (mission board)."""
        mission = random.choice(MISSIONS)
        embed = discord.Embed(
            title="📜 Mission Board",
            description=f"**{mission['name']}**\nReward: {mission['xp']} XP | {mission['gold']} Gold\n\nUse `!accept` to take this mission.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

        async with aiosqlite.connect("database.db") as db:
            await db.execute("DELETE FROM missions WHERE user_id = ?", (ctx.author.id,))
            await db.execute(
                "INSERT INTO missions (user_id, mission_name, xp_reward, gold_reward, completed, solo) VALUES (?, ?, ?, ?, ?, ?)",
                (ctx.author.id, mission["name"], mission["xp"], mission["gold"], 0, int(mission["solo"]))
            )
            await db.commit()

    @commands.command()
    async def accept(self, ctx):
        """Accept your current mission."""
        async with aiosqlite.connect("database.db") as db:
            async with db.execute(
                "SELECT mission_name, solo FROM missions WHERE user_id = ? AND completed = 0", (ctx.author.id,)
            ) as cursor:
                mission = await cursor.fetchone()

        if not mission:
            await ctx.send("No mission to accept. Use `!missions` first.")
            return

        msg = f"✅ You accepted the mission: **{mission[0]}**!"
        if not mission[1]:
            msg += "\nThis mission is co-op! Others can join with `!joinmission @user`."
        await ctx.send(msg)

    # ---------------- COMPLETE MISSION ----------------
    @commands.command()
    async def complete(self, ctx):
        user_id = ctx.author.id
        now = int(time.time())

        async with aiosqlite.connect("database.db") as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                player = await cursor.fetchone()

            if not player:
                await ctx.send("You haven’t been reborn yet! Use `!reborn` first.")
                return

            last_time = player[-1] or 0  # last_mission
            if now - last_time < MISSION_COOLDOWN:
                remaining = MISSION_COOLDOWN - (now - last_time)
                minutes, seconds = divmod(remaining, 60)
                await ctx.send(f"⏳ Wait {minutes}m {seconds}s before completing another mission.")
                return

            async with db.execute(
                "SELECT mission_name, xp_reward, gold_reward, completed FROM missions WHERE user_id = ?", (user_id,)
            ) as cursor:
                mission = await cursor.fetchone()

            if not mission or mission[3]:
                await ctx.send("No active mission to complete. Get a new one with `!missions`.")
                return

            name, xp, gold, _ = mission
            xp, gold = apply_class_bonus(player[5], xp, gold)

            new_xp = player[3] + xp
            new_gold = player[4] + gold

            await db.execute(
                "UPDATE players SET xp = ?, gold = ?, last_mission = ? WHERE user_id = ?",
                (new_xp, new_gold, now, user_id)
            )
            await db.execute("UPDATE missions SET completed = 1 WHERE user_id = ?", (user_id,))
            await db.commit()

        embed = discord.Embed(
            title="🏆 Mission Complete!",
            description=f"**{ctx.author.display_name}** completed **{name}**!",
            color=discord.Color.green()
        )
        embed.add_field(name="XP Gained", value=f"+{xp}")
        embed.add_field(name="Gold Earned", value=f"+{gold}")
        await ctx.send(embed=embed)

    # ---------------- DUELS ----------------
    @commands.command()
    async def duel(self, ctx, target: discord.Member):
        if target.bot or target == ctx.author:
            await ctx.send("Cannot duel bots or yourself.")
            return

        async with aiosqlite.connect("database.db") as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (ctx.author.id,)) as cursor:
                challenger = await cursor.fetchone()
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (target.id,)) as cursor:
                defender = await cursor.fetchone()

            if not challenger or not defender:
                await ctx.send("Both players must be reborn first!")
                return

            winner, loser = (challenger, defender) if random.random() < 0.5 else (defender, challenger)
            xp_gain = random.randint(20, 50)
            gold_gain = random.randint(10, 50)
            xp_gain, gold_gain = apply_class_bonus(winner[5], xp_gain, gold_gain)

            await db.execute(
                "UPDATE players SET xp = ?, gold = ? WHERE user_id = ?",
                (winner[3] + xp_gain, winner[4] + gold_gain, winner[0])
            )
            await db.commit()

        await ctx.send(f"⚔️ Duel Result: {winner[1]} defeats {loser[1]}! +{xp_gain} XP, +{gold_gain} Gold")

    # ---------------- MINI GAME ----------------
    @commands.command()
    async def roll(self, ctx):
        result = random.randint(1, 6)
        xp = result * 5
        gold = result * 10
        async with aiosqlite.connect("database.db") as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (ctx.author.id,)) as cursor:
                player = await cursor.fetchone()
            if not player:
                await ctx.send("Reborn first!")
                return
            xp, gold = apply_class_bonus(player[5], xp, gold)
            await db.execute(
                "UPDATE players SET xp = ?, gold = ? WHERE user_id = ?",
                (player[3] + xp, player[4] + gold, player[0])
            )
            await db.commit()
        await ctx.send(f"🎲 You rolled a {result}! +{xp} XP, +{gold} Gold")

async def setup(bot):
    await bot.add_cog(Quests(bot))