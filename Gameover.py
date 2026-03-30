 def _show_gameover(self):
        self.canvas.delete("overlay")
        self._dim()
        new_high = self.score > 0 and self.score == self.high

        self.canvas.create_text(WIDTH//2, 110,
            text="GAME OVER", fill=FOOD_COLOR,
            font=("Courier New", 40, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 180,
            text=f"SCORE: {self.score}", fill=GREEN,
            font=("Courier New", 24, "bold"), tags="overlay")
        self.canvas.create_text(WIDTH//2, 225,
            text=f"LENGTH: {len(self.body)}  /  {MAX_LENGTH}", fill=DIM_GREEN,
            font=("Courier New", 13, "bold"), tags="overlay")

        if new_high and self.score > 0:
            self.canvas.create_text(WIDTH//2, 268,
                text="★  NEW BEST SCORE!  ★", fill=AMBER,
                font=("Courier New", 14, "bold"), tags="overlay")

        self.canvas.create_text(WIDTH//2, 320,
            text=f"BEST: {self.high}", fill=DARK_GREEN,
            font=("Courier New", 13, "bold"), tags="overlay")

        self.canvas.create_line(60, GAME_H-70, WIDTH-60, GAME_H-70,
            fill=DIM_GREEN, tags="overlay")
        self._blink_id = self.canvas.create_text(WIDTH//2, GAME_H - 42,
            text="[ SPACE = retry  |  R = new game ]", fill=AMBER,
            font=("Courier New", 13, "bold"), tags=("overlay", "blink"))