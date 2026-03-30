# ── wall_collision.py ────────────────────────────────────────────────────────
# Lose condition: game ends if the snake's head moves outside the board.

from constants import COLS, ROWS


def check_wall_collision(head: tuple) -> bool:
    """Return True if the head position is outside the grid boundaries."""
    x, y = head
    return not (0 <= x < COLS and 0 <= y < ROWS)
