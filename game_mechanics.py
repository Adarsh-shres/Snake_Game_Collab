# ── game_mechanics.py ────────────────────────────────────────────────────────
# Core game mechanics: movement, speed scaling, and win condition check.

from constants import BASE_DELAY, MIN_DELAY, SPEED_STEP, MAX_LENGTH


# ── Movement ──────────────────────────────────────────────────────────────────

# Maps key names to (dx, dy) direction vectors.
DIRECTION_KEYS = {
    "up":    (0, -1), "w": (0, -1),
    "down":  (0,  1), "s": (0,  1),
    "left":  (-1, 0), "a": (-1, 0),
    "right": (1,  0), "d": (1,  0),
}


def get_next_head(body: list[tuple], direction: tuple) -> tuple:
    """Return the grid position the head will move to next."""
    hx, hy = body[0]
    dx, dy = direction
    return (hx + dx, hy + dy)


def is_reverse(new_dir: tuple, current_dir: tuple) -> bool:
    """Return True if new_dir is directly opposite to current_dir (not allowed)."""
    return (new_dir[0] + current_dir[0], new_dir[1] + current_dir[1]) == (0, 0)


# ── Speed ─────────────────────────────────────────────────────────────────────

def calc_delay(body: list[tuple]) -> int:
    """Return the tick delay in ms based on current snake length.

    Speed increases with every segment beyond the starting length of 3.
    Delay is clamped to MIN_DELAY so the game never becomes unplayable.
    """
    extra = len(body) - 3
    return max(MIN_DELAY, BASE_DELAY - extra * SPEED_STEP)


def speed_label(body: list[tuple]) -> str:
    """Return a human-readable speed label for the HUD."""
    delay = calc_delay(body)
    if delay > 140: return "SLOW"
    if delay > 100: return "MEDIUM"
    if delay > 70:  return "FAST"
    if delay > 50:  return "BLAZING"
    return "MAX"


# ── Win condition ─────────────────────────────────────────────────────────────

def check_win(body: list[tuple]) -> bool:
    """Return True if the snake has filled every cell on the board."""
    return len(body) >= MAX_LENGTH
