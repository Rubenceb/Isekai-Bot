import random
from discord.ext import commands
from utils import get_player, update_player, xp_for_next_level
from classes import apply_class_bonus

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        user = await get_player(message.author.id)
        if not user:
            return

        base_xp = random.randint(10, 20)
        base_gold = random.randint(5, 10)
        xp_gain, gold_gain = apply_class_bonus(user[5], base_xp, base_gold)

        new_xp = user[3] + xp_gain
        new_gold = user[4] + gold_gain
        level = user[2]
        leveled_up = False

        while new_xp >= xp_for_next_level(level):
            new_xp -= xp_for_next_level(level)
            level += 1
            leveled_up = True

        await update_player(user[0], xp=new_xp, gold=new_gold, level=level)

        if leveled_up:
            await message.channel.send(f"🎉 {message.author.mention} leveled up to **Level {level}!**")

async def setup(bot):
    await bot.add_cog(Economy(bot))
