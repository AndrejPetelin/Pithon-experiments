"""
Frank's Diner - Core Data Models
"""

from dataclasses import dataclass, field


@dataclass
class Response:
    """
    One of Frank's possible replies in an interaction.
    texts       : list of variations, one picked at runtime
    effects     : list of (stat, delta) tuples e.g. [("humor", 2), ("suspicion", -3)]
    """
    id:      str
    texts:   list[str]               = field(default_factory=list)
    effects: list[tuple[str, int]]   = field(default_factory=list)

    def __repr__(self):
        effects_str = " ".join(f"{s}{'+' if d > 0 else ''}{d}" for s, d in self.effects)
        return f"Response({self.id!r}, texts={len(self.texts)}, effects=[{effects_str}])"


@dataclass
class Interaction:
    """
    One exchange unit — an NPC/agent line and all valid Frank responses.
    id        : unique string key
    lines     : NPC line variations, one picked at runtime
    responses : all Response objects belonging to this interaction
    """
    id:        str
    lines:     list[str]               = field(default_factory=list)
    responses: list[Response]          = field(default_factory=list)

    def get_response(self, response_id: str) -> Response | None:
        """Look up a response by id."""
        for r in self.responses:
            if r.id == response_id:
                return r
        return None

    def response_ids(self) -> list[str]:
        """Return all response ids in this interaction."""
        return [r.id for r in self.responses]

    def __repr__(self):
        return (f"Interaction({self.id!r}, "
                f"lines={len(self.lines)}, "
                f"responses={self.response_ids()})")


# ── quick sanity check ────────────────────────────────────────────────────────
if __name__ == "__main__":
    r1 = Response(
        id="girlfriend_safe",
        texts=["Don't worry, I'm sure your girlfriend is safe."],
        effects=[("humor", 2), ("suspicion", -3), ("confidence", 1)]
    )

    r2 = Response(
        id="deny_knowledge",
        texts=["I wouldn't know anything about that."],
        effects=[("suspicion", 1), ("deflection", 1)]
    )

    interaction = Interaction(
        id="cow_rumors",
        lines=[
            "There are rumors of cow kidnapping by a flying saucer.",
            "We've had reports of livestock disappearing under unusual circumstances.",
        ],
        responses=[r1, r2]
    )

    print(interaction)
    print(interaction.get_response("girlfriend_safe"))
    print(interaction.get_response("nonexistent"))
