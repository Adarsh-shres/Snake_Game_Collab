import tkinter as tk
from tkinter import simpledialog
import random
import json
import os

# ── Constants ────────────────────────────────────────────────────────────────
COLS, ROWS   = 20, 20
CELL         = 28
WIDTH        = COLS * CELL        # 560
HUD          = 50
GAME_H       = ROWS * CELL        # 560
HEIGHT       = GAME_H + HUD       # 610
LB_FILE      = "leaderboard.json"
MAX_ENTRIES  = 10

BG         = "#020c02"
GRID       = "#041504"
GREEN      = "#00ff41"
DARK_GREEN = "#00b32c"
DIM_GREEN  = "#1a3d1a"
HEAD_COLOR = "#afffca"
FOOD_COLOR = "#ff3131"
AMBER      = "#ffb700"
GOLD       = "#ffd700"
SILVER     = "#c0c0c0"
BRONZE     = "#cd7f32"
BLACK      = "#000000"


# ── Leaderboard helpers ───────────────────────────────────────────────────────
def load_leaderboard():
    if os.path.exists(LB_FILE):
        try:
            with open(LB_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_leaderboard(lb):
    with open(LB_FILE, "w") as f:
        json.dump(lb, f, indent=2)


def add_entry(lb, name, score, level):
    lb.append({"name": name[:12], "score": score, "level": level})
    lb.sort(key=lambda e: e["score"], reverse=True)
    return lb[:MAX_ENTRIES]


def get_rank(lb, score):
    """Return 1-based rank of this score in current leaderboard (before insertion)."""
    for i, e in enumerate(lb):
        if score >= e["score"]:
            return i + 1
    return len(lb) + 1


# ── Main game class ───────────────────────────────────────────────────────────
class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("SNAKE.PY")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.leaderboard = load_leaderboard()

        # ── HUD ──────────────────────────────────────────────────────────────
        self.hud = tk.Canvas(root, width=WIDTH, height=HUD,
                             bg="#020802", highlightthickness=0)
        self.hud.pack()
        self.score_txt = self.hud.create_text(
            20, HUD//2, anchor="w", fill=GREEN,
            font=("Courier New", 14, "bold"), text="SCORE: 0")
        best = self.leaderboard[0]["score"] if self.leaderboard else 0
        self.high_txt = self.hud.create_text(
            WIDTH//2, HUD//2, anchor="center", fill=DARK_GREEN,
            font=("Courier New", 14, "bold"), text=f"BEST: {best}")
        self.level_txt = self.hud.create_text(
            WIDTH-20, HUD//2, anchor="e", fill=GREEN,
            font=("Courier New", 14, "bold"), text="LVL: 1")
        self.hud.create_line(0, HUD-1, WIDTH, HUD-1, fill=DIM_GREEN)

        # ── Game canvas ──────────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, width=WIDTH, height=GAME_H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        # ── State ────────────────────────────────────────────────────────────
        self.state      = "idle"
        self.blink_on   = True
        self._blink_job = None
        self._game_job  = None

        self._draw_grid()
        self._show_main_overlay()
        self._start_blink()

        root.bind("<KeyPress>", self.on_key)
        root.focus_set()

    # ── Grid ─────────────────────────────────────────────────────────────────
    def _draw_grid(self):
        for x in range(COLS + 1):
            self.canvas.create_line(x*CELL, 0, x*CELL, GAME_H,
                                    fill=GRID, tags="grid")
        for y in range(ROWS + 1):
            self.canvas.create_line(0, y*CELL, WIDTH, y*CELL,
                                    fill=GRID, tags="grid")

    # ── Game init ─────────────────────────────────────────────────────────────
    def new_game(self):
        self.canvas.delete("snake", "food", "overlay")
        self.body  = [(10, 10), (9, 10), (8, 10)]
        self.dir   = (1, 0)
        self.next  = (1, 0)
        self.score = 0
        self.level = 1
        self.delay = 150
        self._update_hud()
        self._spawn_food()
        self._draw_snake()
        self._draw_food()

    def _spawn_food(self):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in self.body:
                self.food = pos
                break

    # ── Drawing ───────────────────────────────────────────────────────────────
    def _draw_snake(self):
        self.canvas.delete("snake")
        n = len(self.body)
        for i, (cx, cy) in enumerate(self.body):
            x1, y1 = cx*CELL + 2, cy*CELL + 2
            x2, y2 = x1 + CELL - 4, y1 + CELL - 4
            if i == 0:
                self.canvas.create_rectangle(x1-2, y1-2, x2+2, y2+2,
                    fill="#1a4a2a", outline="", tags="snake")
                self.canvas.create_rectangle(x1, y1, x2, y2,
                    fill=HEAD_COLOR, outline="", tags="snake")
                self._draw_eyes(cx, cy)
            else:
                t   = i / n
                g   = int(179 - 140 * t)
                b   = int(44  - 35  * t)
                self.canvas.create_rectangle(x1+1, y1+1, x2-1, y2-1,
                    fill=f"#00{g:02x}{b:02x}", outline="", tags="snake")

    def _draw_eyes(self, cx, cy):
        dx, dy = self.dir
        if   dx ==  1: eyes = [(cx*CELL+CELL-7, cy*CELL+5),      (cx*CELL+CELL-7, cy*CELL+CELL-8)]
        elif dx == -1: eyes = [(cx*CELL+4,       cy*CELL+5),      (cx*CELL+4,       cy*CELL+CELL-8)]
        elif dy == -1: eyes = [(cx*CELL+5,        cy*CELL+4),      (cx*CELL+CELL-8,  cy*CELL+4)]
        else:          eyes = [(cx*CELL+5,        cy*CELL+CELL-7), (cx*CELL+CELL-8,  cy*CELL+CELL-7)]
        for ex, ey in eyes:
            self.canvas.create_rectangle(ex, ey, ex+2, ey+2,
                fill=BLACK, outline="", tags="snake")

    def _draw_food(self):
        self.canvas.delete("food")
        cx, cy = self.food
        fx, fy = cx*CELL + CELL//2, cy*CELL + CELL//2
        r = CELL // 3
        self.canvas.create_oval(fx-r-4, fy-r-4, fx+r+4, fy+r+4,
            fill="#3d0000", outline="", tags="food")
        self.canvas.create_oval(fx-r, fy-r, fx+r, fy+r,
            fill=FOOD_COLOR, outline="", tags="food")

    def _update_hud(self):
        best = self.leaderboard[0]["score"] if self.leaderboard else 0
        self.hud.itemconfig(self.score_txt, text=f"SCORE: {self.score}")
        self.hud.itemconfig(self.high_txt,  text=f"BEST:  {best}")
        self.hud.itemconfig(self.level_txt, text=f"LVL:   {self.level}")

    # ── Overlays ──────────────────────────────────────────────────────────────
    def _dim_bg(self):
        self.canvas.create_rectangle(0, 0, WIDTH, GAME_H,
            fill=BG, stipple="gray50", outline="", tags="overlay")
        self.canvas.create_rectangle(0, 0, WIDTH, GAME_H,
            fill=BG, stipple="gray50", outline="", tags="overlay")

    def _show_main_overlay(self):
        """Idle screen: title + leaderboard preview."""
        self.canvas.delete("overlay")
        self._dim_bg()

        self.canvas.create_text(WIDTH//2, 60, text="SNAKE",
            fill=GREEN, font=("Courier New", 48, "bold"), tags="overlay")

        # Mini leaderboard on idle screen
        self.canvas.create_text(WIDTH//2, 125, text="─── TOP SCORES ───",
            fill=DIM_GREEN, font=("Courier New", 11, "bold"), tags="overlay")

        medals = [GOLD, SILVER, BRONZE]
        for i, entry in enumerate(self.leaderboard[:5]):
            col = medals[i] if i < 3 else DARK_GREEN
            row = f"#{i+1}  {entry['name']:<12}  {entry['score']:>4}"
            self.canvas.create_text(WIDTH//2, 150 + i*22, text=row,
                fill=col, font=("Courier New", 12, "bold"), tags="overlay")

        if not self.leaderboard:
            self.canvas.create_text(WIDTH//2, 160, text="No scores yet!",
                fill=DIM_GREEN, font=("Courier New", 12), tags="overlay")

        self.canvas.create_text(WIDTH//2, 285,
            text="ARROW KEYS or WASD to move", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")
        self.canvas.create_text(WIDTH//2, 305,
            text="L = leaderboard   Q = quit", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")

        self._blink_id = self.canvas.create_text(WIDTH//2, 340,
            text="[ PRESS SPACE TO START ]", fill=AMBER,
            font=("Courier New", 15, "bold"), tags=("overlay", "blink"))

    def _show_leaderboard(self):
        """Full leaderboard screen."""
        self.canvas.delete("overlay")
        self._dim_bg()

        self.canvas.create_text(WIDTH//2, 45, text="LEADERBOARD",
            fill=GREEN, font=("Courier New", 30, "bold"), tags="overlay")
        self.canvas.create_line(60, 75, WIDTH-60, 75,
            fill=DIM_GREEN, tags="overlay")

        # Header
        self.canvas.create_text(WIDTH//2, 95,
            text=f"{'#':<3}  {'NAME':<12}  {'SCORE':>5}  {'LVL':>4}",
            fill=DIM_GREEN, font=("Courier New", 12, "bold"), tags="overlay")

        medals = [GOLD, SILVER, BRONZE]
        for i, entry in enumerate(self.leaderboard):
            col = medals[i] if i < 3 else (GREEN if i < 5 else DARK_GREEN)
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            row = f"{str(i+1)+'.':<3}  {entry['name']:<12}  {entry['score']:>5}  {entry['level']:>4}"
            self.canvas.create_text(WIDTH//2, 122 + i*28, text=row,
                fill=col, font=("Courier New", 13, "bold"), tags="overlay")

        if not self.leaderboard:
            self.canvas.create_text(WIDTH//2, 200,
                text="No scores yet — play a game!",
                fill=DIM_GREEN, font=("Courier New", 13), tags="overlay")

        self.canvas.create_line(60, GAME_H-70, WIDTH-60, GAME_H-70,
            fill=DIM_GREEN, tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H-45,
            text="[ PRESS SPACE TO PLAY  |  C = CLEAR ]", fill=AMBER,
            font=("Courier New", 13, "bold"), tags=("overlay", "blink"))

    def _show_gameover(self, is_new_high, rank):
        self.canvas.delete("overlay")
        self._dim_bg()

        self.canvas.create_text(WIDTH//2, 90, text="GAME OVER",
            fill=FOOD_COLOR, font=("Courier New", 38, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 150,
            text=f"SCORE: {self.score}", fill=GREEN,
            font=("Courier New", 22, "bold"), tags="overlay")

        if is_new_high:
            self.canvas.create_text(WIDTH//2, 188,
                text="★  NEW HIGH SCORE!  ★", fill=GOLD,
                font=("Courier New", 15, "bold"), tags="overlay")
        elif self.score > 0:
            self.canvas.create_text(WIDTH//2, 188,
                text=f"RANK #{rank} on leaderboard", fill=AMBER,
                font=("Courier New", 13, "bold"), tags="overlay")

        # Mini leaderboard
        self.canvas.create_text(WIDTH//2, 230, text="─── TOP SCORES ───",
            fill=DIM_GREEN, font=("Courier New", 11, "bold"), tags="overlay")
        medals = [GOLD, SILVER, BRONZE]
        for i, entry in enumerate(self.leaderboard[:5]):
            col = medals[i] if i < 3 else DARK_GREEN
            marker = " ◄" if entry.get("_new") else ""
            row = f"#{i+1}  {entry['name']:<12}  {entry['score']:>4}{marker}"
            self.canvas.create_text(WIDTH//2, 255 + i*22, text=row,
                fill=col, font=("Courier New", 12, "bold"), tags="overlay")

        self.canvas.create_text(WIDTH//2, 375,
            text="L = full leaderboard", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, 405,
            text="[ SPACE = retry  |  R = restart ]", fill=AMBER,
            font=("Courier New", 13, "bold"), tags=("overlay", "blink"))

    def _show_simple_overlay(self, title, blink_text):
        self.canvas.delete("overlay")
        self._dim_bg()
        self.canvas.create_text(WIDTH//2, GAME_H//2 - 40, text=title,
            fill=GREEN, font=("Courier New", 42, "bold"), tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H//2 + 30,
            text=blink_text, fill=AMBER,
            font=("Courier New", 15, "bold"), tags=("overlay", "blink"))

    def _start_blink(self):
        self.blink_on = not self.blink_on
        color = AMBER if self.blink_on else BG
        try:
            self.canvas.itemconfig("blink", fill=color)
        except Exception:
            pass
        self._blink_job = self.root.after(500, self._start_blink)

    # ── Game loop ─────────────────────────────────────────────────────────────
    def _step(self):
        self.dir = self.next
        hx, hy  = self.body[0]
        head    = (hx + self.dir[0], hy + self.dir[1])

        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in self.body:
            self._die()
            return

        self.body.insert(0, head)
        if head == self.food:
            self.score += 1
            self.level  = self.score // 5 + 1
            self.delay  = max(60, 150 - (self.level - 1) * 12)
            self._spawn_food()
            self._draw_food()
        else:
            self.body.pop()

        self._update_hud()
        self._draw_snake()
        self._game_job = self.root.after(self.delay, self._step)

    def _die(self):
        self.state = "dead"

        if self.score > 0:
            rank      = get_rank(self.leaderboard, self.score)
            qualifies = len(self.leaderboard) < MAX_ENTRIES or self.score >= (self.leaderboard[-1]["score"] if self.leaderboard else 0)

            if qualifies:
                # Ask for name — pause the blink loop briefly
                name = simpledialog.askstring(
                    "Nice score!",
                    f"You scored {self.score}!\nEnter your name for the leaderboard:",
                    parent=self.root) or "PLAYER"
                name = name.strip() or "PLAYER"

                # Mark new entry temporarily
                for e in self.leaderboard:
                    e.pop("_new", None)
                self.leaderboard = add_entry(self.leaderboard, name, self.score, self.level)
                for e in self.leaderboard:
                    if e["name"] == name[:12] and e["score"] == self.score:
                        e["_new"] = True
                        break
                save_leaderboard(self.leaderboard)

                is_new_high = self.leaderboard[0].get("_new", False)
                final_rank  = next((i+1 for i,e in enumerate(self.leaderboard) if e.get("_new")), rank)
            else:
                is_new_high = False
                final_rank  = rank
        else:
            is_new_high = False
            final_rank  = MAX_ENTRIES + 1

        self._update_hud()
        self._show_gameover(is_new_high, final_rank)

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key(self, event):
        k = event.keysym.lower()

        # Movement
        dirs = {"up":(0,-1),"w":(0,-1),"down":(0,1),"s":(0,1),
                "left":(-1,0),"a":(-1,0),"right":(1,0),"d":(1,0)}
        if k in dirs and self.state == "running":
            nd = dirs[k]
            if (nd[0]+self.dir[0], nd[1]+self.dir[1]) != (0,0):
                self.next = nd

        # Space = start / pause / resume / retry
        if k == "space":
            if self.state in ("idle", "dead", "leaderboard"):
                for e in self.leaderboard:
                    e.pop("_new", None)
                self.state = "running"
                self.new_game()
                self._step()
            elif self.state == "running":
                self.state = "paused"
                if self._game_job:
                    self.root.after_cancel(self._game_job)
                self._show_simple_overlay("PAUSED", "[ PRESS SPACE TO RESUME ]")
            elif self.state == "paused":
                self.state = "running"
                self.canvas.delete("overlay")
                self._step()

        # L = leaderboard
        if k == "l" and self.state in ("idle", "dead", "leaderboard"):
            self.state = "leaderboard"
            self._show_leaderboard()

        # C = clear leaderboard (only on leaderboard screen)
        if k == "c" and self.state == "leaderboard":
            self.leaderboard = []
            save_leaderboard(self.leaderboard)
            self._update_hud()
            self._show_leaderboard()

        # R = restart
        if k == "r" and self.state not in ("idle",):
            if self._game_job:
                self.root.after_cancel(self._game_job)
            for e in self.leaderboard:
                e.pop("_new", None)
            self.state = "running"
            self.new_game()
            self._step()

        # Q = quit
        if k == "q":
            self.root.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
