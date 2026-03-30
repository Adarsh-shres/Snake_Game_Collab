# ── Constants ────────────────────────────────────────────────────────────────
COLS, ROWS = 20, 20
CELL       = 28
WIDTH      = COLS * CELL        # 560
HUD        = 50
HEIGHT     = ROWS * CELL + HUD  # 610

BG         = "#020c02"
GRID       = "#041504"
GREEN      = "#00ff41"
DARK_GREEN = "#00b32c"
DIM_GREEN  = "#1a3d1a"
HEAD_COLOR = "#afffca"
FOOD_COLOR = "#ff3131"
AMBER      = "#ffb700"
BLACK      = "#000000"


def _draw_snake(self):
        self.canvas.delete("snake")
        n = len(self.body)
        for i, (cx, cy) in enumerate(self.body):
            x1, y1 = cx*CELL + 2, cy*CELL + 2
            x2, y2 = x1 + CELL - 4, y1 + CELL - 4

            if i == 0:
                # Glow effect (slightly larger box behind)
                self.canvas.create_rectangle(
                    x1-2, y1-2, x2+2, y2+2,
                    fill="#1a4a2a", outline="", tags="snake")
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=HEAD_COLOR, outline="", tags="snake")
                self._draw_eyes(cx, cy)
            else:
                t   = i / n
                g   = int(179 - 140 * t)
                b   = int(44  - 35  * t)
                col = f"#00{g:02x}{b:02x}"
                self.canvas.create_rectangle(
                    x1+1, y1+1, x2-1, y2-1,
                    fill=col, outline="", tags="snake")
