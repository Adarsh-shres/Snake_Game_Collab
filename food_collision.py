# ── food_collision.py ────────────────────────────────────────────────────────
# Handles food spawning and detecting when the snake's head touches food.

import random
from constants import COLS, ROWS


def spawn_food(body: list[tuple]) -> tuple:
    """Return a random grid position that is not occupied by the snake body."""
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in body:
            return pos


def check_food_collision(head: tuple, food: tuple) -> bool:
    """Return True if the snake's head has reached the food position."""
    return head == food
