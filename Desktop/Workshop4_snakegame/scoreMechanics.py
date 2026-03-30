#Score_Logic
def _draw_food(self):
        self.canvas.delete("food")
        cx, cy = self.food
        fx, fy = cx*CELL + CELL//2, cy*CELL + CELL//2
        r = CELL // 3
        self.canvas.create_oval(fx-r-4, fy-r-4, fx+r+4, fy+r+4,
            fill="#3d0000", outline="", tags="food")
        self.canvas.create_oval(fx-r, fy-r, fx+r, fy+r,
            fill=FOOD_COLOR, outline="", tags="food")
#Score_Display
    def _update_hud(self):
        best = self.leaderboard[0]["score"] if self.leaderboard else 0
        self.hud.itemconfig(self.score_txt, text=f"SCORE: {self.score}")
        self.hud.itemconfig(self.high_txt,  text=f"BEST:  {best}")
        self.hud.itemconfig(self.level_txt, text=f"LVL:   {self.level}")

#Score_used_in_Game_Over:
self.canvas.create_text(WIDTH//2, 150,
    text=f"SCORE: {self.score}", fill=GREEN,
    font=("Courier New", 22, "bold"), tags="overlay")
