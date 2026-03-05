"""
Frank's Diner - Character
Owns and manages a character's stats during a conversation.
"""

from dataclasses import dataclass, field


@dataclass
class Character:
    """
    Tracks a character's stats across interactions.
    stats are created dynamically as effects are applied,
    so no need to predefine which stats exist.
    """
    id:    str
    name:  str
    stats: dict[str, int] = field(default_factory=dict)

    def apply_effects(self, effects: list[tuple[str, int]]) -> None:
        """Apply a response's effects to this character's stats."""
        for stat, delta in effects:
            self.stats[stat] = self.stats.get(stat, 0) + delta

    def get_stat(self, stat: str) -> int:
        """Return a stat value, defaulting to 0 if not yet set."""
        return self.stats.get(stat, 0)

    def reset(self) -> None:
        """Clear all stats back to zero."""
        self.stats.clear()

    def __repr__(self):
        stats_str = " ".join(f"{k}={v:+d}" for k, v in self.stats.items())
        return f"Character({self.name!r}, [{stats_str}])"


# ── quick sanity check ────────────────────────────────────────────────────────
if __name__ == "__main__":
    frank = Character(id="frank", name="Frank")

    print(f"Before: {frank}")

    frank.apply_effects([("humor", 2), ("suspicion", -3), ("confidence", 1)])
    print(f"After girlfriend_safe: {frank}")

    frank.apply_effects([("suspicion", 1), ("deflection", 1)])
    print(f"After deny_knowledge: {frank}")

    print(f"Suspicion: {frank.get_stat('suspicion')}")
    print(f"Charm (never set): {frank.get_stat('charm')}")
