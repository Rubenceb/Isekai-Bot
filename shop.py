import json
import discord
from discord.ext import commands
from utils import get_player, update_player

ITEMS = {
    "Potion": {"price": 50, "desc": "Restores 50 XP (placeholder)."},
    "Mana Scroll": {"price": 100, "desc": "Boosts XP gain temporarily."},
    "Iron Sword": {"price": 250, "desc": "Increases XP gain by 10% (passive)."}
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- SHOP LIST ----------------
    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="🛒 Isekai Shop", color=discord.Color.gold())
        for name, info in ITEMS.items():
            embed.add_field(name=f"{name} — {info['price']} gold", value=info['desc'], inline=False)
        await ctx.send(embed=embed)

    # ---------------- BUY COMMAND ----------------
    @commands.command()
    async def buy(self, ctx, *, item_name: str = None):
        if not item_name:
            await ctx.send("Usage: `!buy <item name>`")
            return

        user = await get_player(ctx.author.id)
        print(f"[DEBUG] !buy triggered by {ctx.author} | DB user: {user}")

        if not user:
            await ctx.send("You need to be reborn first! Use `!reborn`.")
            return

        item_name = item_name.title()
        if item_name not in ITEMS:
            await ctx.send("Item not found in the shop.")
            return

        item = ITEMS[item_name]
        user_gold = user[4] if user[4] is not None else 0

        if user_gold < item["price"]:
            await ctx.send(f"💰 You don’t have enough gold to buy a {item_name}.")
            return

        # Inventory handling
        try:
            inventory = json.loads(user[6] if user[6] else "{}")
        except Exception as e:
            print(f"[ERROR] Could not parse inventory JSON for {ctx.author}: {e}")
            inventory = {}

        inventory[item_name] = inventory.get(item_name, 0) + 1

        # Update DB
        new_gold = user_gold - item["price"]
        await update_player(ctx.author.id, gold=new_gold, inventory=json.dumps(inventory))

        print(f"[DEBUG] Updated {ctx.author}: gold={new_gold}, inventory={inventory}")
        await ctx.send(f"✅ You bought a **{item_name}** for **{item['price']} gold!**")

    # ---------------- INVENTORY COMMAND ----------------
    @commands.command()
    async def inventory(self, ctx):
        user = await get_player(ctx.author.id)
        print(f"[DEBUG] !inventory triggered by {ctx.author} | DB user: {user}")

        if not user:
            await ctx.send("You need to be reborn first! Use `!reborn`.")
            return

        try:
            inventory = json.loads(user[6] if user[6] else "{}")
        except Exception as e:
            print(f"[ERROR] Could not parse inventory JSON for {ctx.author}: {e}")
            inventory = {}

        if not inventory:
            await ctx.send("👜 Your inventory is empty.")
            return

        embed = discord.Embed(title=f"{ctx.author.display_name}'s Inventory", color=discord.Color.blue())
        for item, qty in inventory.items():
            embed.add_field(name=item, value=f"x{qty}", inline=True)

        await ctx.send(embed=embed)


# ---------------- SETUP FUNCTION ----------------
async def setup(bot):
    await bot.add_cog(Shop(bot))
    print("✅ Shop Cog loaded successfully")
