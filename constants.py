# ── constants.py ─────────────────────────────────────────────────────────────
# Shared constants used across all modules.

COLS, ROWS = 20, 20
CELL       = 28
WIDTH      = COLS * CELL   # 560
HUD        = 50
GAME_H     = ROWS * CELL   # 560

# Colours
BG         = "#020c02"
GRID       = "#041504"
GREEN      = "#00ff41"
DARK_GREEN = "#00b32c"
DIM_GREEN  = "#1a3d1a"
HEAD_COLOR = "#afffca"
FOOD_COLOR = "#ff3131"
AMBER      = "#ffb700"
WIN_COLOR  = "#ffe066"
BLACK      = "#000000"

# Speed / win
BASE_DELAY = 180          # ms at starting length (3 segments)
MIN_DELAY  = 40           # ms floor (fastest possible)
SPEED_STEP = 5            # ms reduction per extra segment grown
MAX_LENGTH = COLS * ROWS  # 400 — fill every cell to win
