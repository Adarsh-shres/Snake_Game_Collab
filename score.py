# ── score.py ─────────────────────────────────────────────────────────────────
# Manages the player's score and all-time high score.


class ScoreManager:
    def __init__(self):
        self.score = 0
        self.high  = 0

    def reset(self):
        """Reset current score to zero (call at the start of each game)."""
        self.score = 0

    def increment(self):
        """Add one point (call when food is eaten) and update the high score."""
        self.score += 1
        if self.score > self.high:
            self.high = self.score

    def is_new_high(self) -> bool:
        """Return True if the current score equals the all-time high (> 0)."""
        return self.score > 0 and self.score == self.high
