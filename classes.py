import random

CLASSES = {
    "⚔️ Warrior": {"xp_mult": 1.2, "gold_mult": 1.0},
    "🧙 Mage": {"xp_mult": 1.0, "gold_mult": 1.25},
    "🦊 Rogue": {"xp_mult": 1.0, "gold_mult": 1.0},
    "💖 Cleric": {"xp_mult": 1.1, "gold_mult": 1.0}
}

def apply_class_bonus(path, base_xp, base_gold):
    if not path or path not in CLASSES:
        return base_xp, base_gold

    bonuses = CLASSES[path]
    xp = int(base_xp * bonuses.get("xp_mult", 1))
    gold = int(base_gold * bonuses.get("gold_mult", 1))

    # Rogue chance to steal extra gold
    if "Rogue" in path and random.random() < 0.1:
        gold += random.randint(5, 15)

    return xp, gold
