# ── snake.py ─────────────────────────────────────────────────────────────────
# Entry point. Handles rendering and UI; delegates all game logic to modules:
#   constants.py      — shared constants
#   food_collision.py — food spawning and eating detection
#   score.py          — score tracking and high-score management
#   self_collision.py — lose condition: snake hits itself
#   wall_collision.py — lose condition: snake hits the wall
#   game_mechanics.py — movement, speed scaling, win condition

import tkinter as tk

from constants import (
    COLS, ROWS, CELL, WIDTH, HUD, GAME_H,
    BG, GRID, GREEN, DARK_GREEN, DIM_GREEN,
    HEAD_COLOR, FOOD_COLOR, AMBER, WIN_COLOR, BLACK,
    MAX_LENGTH,
)
from food_collision import spawn_food, check_food_collision
from score import ScoreManager
from self_collision import check_self_collision
from wall_collision import check_wall_collision
from game_mechanics import (
    DIRECTION_KEYS, get_next_head, is_reverse,
    calc_delay, speed_label, check_win,
)


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("SNAKE.PY")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.scorer     = ScoreManager()
        self.state      = "idle"
        self.blink_on   = True
        self._blink_job = None
        self._game_job  = None
        self.body       = [(10, 10), (9, 10), (8, 10)]

        # ── HUD ──────────────────────────────────────────────────────────────
        self.hud = tk.Canvas(root, width=WIDTH, height=HUD,
                             bg="#020802", highlightthickness=0)
        self.hud.pack()
        self.score_txt = self.hud.create_text(
            16, HUD//2, anchor="w", fill=GREEN,
            font=("Courier New", 13, "bold"), text="SCORE: 0")
        self.speed_txt = self.hud.create_text(
            WIDTH//2, HUD//2, anchor="center", fill=DIM_GREEN,
            font=("Courier New", 13, "bold"), text="")
        self.high_txt = self.hud.create_text(
            WIDTH-16, HUD//2, anchor="e", fill=DARK_GREEN,
            font=("Courier New", 13, "bold"), text="BEST: 0")
        self.hud.create_line(0, HUD-1, WIDTH, HUD-1, fill=DIM_GREEN)

        # ── Game canvas ──────────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, width=WIDTH, height=GAME_H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self._draw_grid()
        self._show_idle()
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

    # ── New game ──────────────────────────────────────────────────────────────
    def new_game(self):
        self.canvas.delete("snake", "food", "overlay")
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.dir  = (1, 0)
        self.next = (1, 0)
        self.scorer.reset()
        self.food = spawn_food(self.body)          # food_collision
        self._update_hud()
        self._draw_snake()
        self._draw_food()

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
                t = i / n
                g = int(179 - 140 * t)
                b = int(44  - 35  * t)
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

    def _draw_win_snake(self):
        self.canvas.delete("snake")
        for i, (cx, cy) in enumerate(self.body):
            x1, y1 = cx*CELL + 1, cy*CELL + 1
            x2, y2 = x1 + CELL - 2, y1 + CELL - 2
            shade = WIN_COLOR if i % 2 == 0 else AMBER
            self.canvas.create_rectangle(x1, y1, x2, y2,
                fill=shade, outline="", tags="snake")

    def _update_hud(self):
        self.hud.itemconfig(self.score_txt, text=f"SCORE: {self.scorer.score}")
        self.hud.itemconfig(self.high_txt,  text=f"BEST: {self.scorer.high}")
        if self.state == "running":
            label = speed_label(self.body)         # game_mechanics
            delay = calc_delay(self.body)          # game_mechanics
            col = GREEN if delay > 100 else (AMBER if delay > 60 else FOOD_COLOR)
            self.hud.itemconfig(self.speed_txt, text=f"[ {label} ]", fill=col)
        elif self.state == "won":
            self.hud.itemconfig(self.speed_txt, text="[ PERFECT ]", fill=WIN_COLOR)
        else:
            self.hud.itemconfig(self.speed_txt, text="")

    # ── Overlays ──────────────────────────────────────────────────────────────
    def _dim(self):
        for _ in range(2):
            self.canvas.create_rectangle(0, 0, WIDTH, GAME_H,
                fill=BG, stipple="gray50", outline="", tags="overlay")

    def _show_idle(self):
        self.canvas.delete("overlay")
        self._dim()
        cy = GAME_H // 2
        self.canvas.create_text(WIDTH//2, cy - 120,
            text="SNAKE", fill=GREEN,
            font=("Courier New", 52, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy - 40,
            text="Speed increases as you grow!", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy - 15,
            text=f"Fill all {MAX_LENGTH} cells to win!", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy + 25,
            text="ARROW KEYS / WASD  ·  SPACE = pause  ·  R = restart",
            fill=DIM_GREEN, font=("Courier New", 10), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy + 65,
            text=f"BEST: {self.scorer.high}",
            fill=DARK_GREEN, font=("Courier New", 13, "bold"), tags="overlay")
        self.canvas.create_line(60, GAME_H-70, WIDTH-60, GAME_H-70,
            fill=DIM_GREEN, tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H - 42,
            text="[ PRESS SPACE TO START ]", fill=AMBER,
            font=("Courier New", 15, "bold"), tags=("overlay", "blink"))

    def _show_gameover(self):
        self.canvas.delete("overlay")
        self._dim()
        self.canvas.create_text(WIDTH//2, 110,
            text="GAME OVER", fill=FOOD_COLOR,
            font=("Courier New", 40, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 180,
            text=f"SCORE: {self.scorer.score}", fill=GREEN,
            font=("Courier New", 24, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 225,
            text=f"LENGTH: {len(self.body)}  /  {MAX_LENGTH}", fill=DIM_GREEN,
            font=("Courier New", 13, "bold"), tags="overlay")
        if self.scorer.is_new_high():
            self.canvas.create_text(WIDTH//2, 268,
                text="★  NEW BEST SCORE!  ★", fill=AMBER,
                font=("Courier New", 14, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 320,
            text=f"BEST: {self.scorer.high}", fill=DARK_GREEN,
            font=("Courier New", 13, "bold"), tags="overlay")
        self.canvas.create_line(60, GAME_H-70, WIDTH-60, GAME_H-70,
            fill=DIM_GREEN, tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H - 42,
            text="[ SPACE = retry  |  R = new game ]", fill=AMBER,
            font=("Courier New", 13, "bold"), tags=("overlay", "blink"))

    def _show_win(self):
        self.canvas.delete("overlay", "food")
        self._draw_win_snake()
        self._dim()
        cy = GAME_H // 2
        self.canvas.create_text(WIDTH//2, cy - 110,
            text="YOU WIN!", fill=WIN_COLOR,
            font=("Courier New", 52, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy - 38,
            text="P E R F E C T", fill=AMBER,
            font=("Courier New", 20, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy + 10,
            text=f"SCORE: {self.scorer.score}  ·  LENGTH: {MAX_LENGTH}", fill=GREEN,
            font=("Courier New", 13, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, cy + 40,
            text="You filled the entire board!", fill=DIM_GREEN,
            font=("Courier New", 11), tags="overlay")
        self.canvas.create_line(60, GAME_H-70, WIDTH-60, GAME_H-70,
            fill=WIN_COLOR, tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H - 42,
            text="[ SPACE = play again  |  R = menu ]", fill=WIN_COLOR,
            font=("Courier New", 13, "bold"), tags=("overlay", "blink"))

    def _show_paused(self):
        self.canvas.delete("overlay")
        self._dim()
        self.canvas.create_text(WIDTH//2, GAME_H//2 - 30,
            text="PAUSED", fill=GREEN,
            font=("Courier New", 48, "bold"), tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H//2 + 40,
            text="[ PRESS SPACE TO RESUME ]", fill=AMBER,
            font=("Courier New", 14, "bold"), tags=("overlay", "blink"))

    def _start_blink(self):
        self.blink_on = not self.blink_on
        color = (WIN_COLOR if self.state == "won" else AMBER) if self.blink_on else BG
        try:
            self.canvas.itemconfig("blink", fill=color)
        except Exception:
            pass
        self._blink_job = self.root.after(500, self._start_blink)

    # ── Game loop ─────────────────────────────────────────────────────────────
    def _step(self):
        self.dir  = self.next
        head      = get_next_head(self.body, self.dir)   # game_mechanics

        # Lose conditions
        if check_wall_collision(head):                    # wall_collision
            self._die()
            return
        if check_self_collision(head, self.body):         # self_collision
            self._die()
            return

        self.body.insert(0, head)

        if check_food_collision(head, self.food):         # food_collision
            self.scorer.increment()                       # score
            if check_win(self.body):                      # game_mechanics
                self._update_hud()
                self._draw_snake()
                self._win()
                return
            self.food = spawn_food(self.body)             # food_collision
            self._draw_food()
        else:
            self.body.pop()

        self._update_hud()
        self._draw_snake()
        self._game_job = self.root.after(calc_delay(self.body), self._step)

    def _die(self):
        self.state = "dead"
        self._update_hud()
        self._show_gameover()

    def _win(self):
        self.state = "won"
        self._update_hud()
        self._show_win()

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_key(self, event):
        k = event.keysym.lower()

        if k in DIRECTION_KEYS and self.state == "running":  # game_mechanics
            nd = DIRECTION_KEYS[k]
            if not is_reverse(nd, self.dir):                 # game_mechanics
                self.next = nd

        if k == "space":
            if self.state in ("idle", "dead", "won"):
                self.state = "running"
                self.new_game()
                self._step()
            elif self.state == "running":
                self.state = "paused"
                if self._game_job:
                    self.root.after_cancel(self._game_job)
                self._show_paused()
            elif self.state == "paused":
                self.state = "running"
                self.canvas.delete("overlay")
                self._step()

        if k == "r" and self.state != "idle":
            if self._game_job:
                self.root.after_cancel(self._game_job)
            self.state = "idle"
            self.canvas.delete("snake", "food", "overlay")
            self._show_idle()

        if k == "q":
            self.root.destroy()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
