import discord
from discord.ext import commands
import aiosqlite
from utils import setup_db
import asyncio

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await setup_db()
        print(f"🌍 Core Cog: Database ready!")

    @commands.command()
    async def reborn(self, ctx):
        user_id = ctx.author.id
        async with aiosqlite.connect("database.db") as db:
            async with db.execute("SELECT * FROM players WHERE user_id = ?", (user_id,)) as cursor:
                user = await cursor.fetchone()

            if user:
                await ctx.send(f"You are already reincarnated, **{ctx.author.display_name}**! Your path: `{user[5]}`")
                return

            paths = ["⚔️ Warrior", "🧙 Mage", "🦊 Rogue", "💖 Cleric"]
            path_list = "\n".join([f"{i+1}. {p}" for i, p in enumerate(paths)])
            await ctx.send(
                f"🌟 **Welcome, {ctx.author.display_name}!**\n"
                f"Choose your path:\n{path_list}\nType 1-4."
            )

            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isdigit()

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
                choice = int(msg.content)
                if choice < 1 or choice > 4:
                    await ctx.send("Invalid choice!")
                    return
                chosen_path = paths[choice-1]
                await db.execute(
                    "INSERT INTO players (user_id, name, path) VALUES (?, ?, ?)",
                    (user_id, ctx.author.display_name, chosen_path)
                )
                await db.commit()
                await ctx.send(f"✨ You are now a {chosen_path}!")
            except asyncio.TimeoutError:
                await ctx.send("⏳ Time’s up! Try `!reborn` again.")

    @commands.command()
    async def profile(self, ctx):
        from utils import get_player, create_profile_embed
        user = await get_player(ctx.author.id)
        if not user:
            await ctx.send("You haven’t been reborn yet! Use `!reborn`.")
            return
        embed = create_profile_embed(user)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Core(bot))
