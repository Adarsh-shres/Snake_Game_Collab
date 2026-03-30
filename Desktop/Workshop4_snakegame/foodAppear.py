#Food inisilization
def _spawn_food(self):
        while True:
            pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if pos not in self.body:
                self.food = pos
#Drawing Food
def _draw_food(self):
    self.canvas.delete("food")
    cx, cy = self.food

              #Food_appear_on_start_game&_after_snake_eats_food
                self._spawn_food()
                self._draw_food()
