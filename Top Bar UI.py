self.hud = tk.Canvas(root, width=WIDTH, height=HUD,
                     bg="#020802", highlightthickness=0)

self.score_txt = self.hud.create_text(...)
self.speed_txt = self.hud.create_text(...)
self.high_txt  = self.hud.create_text(...)

self.hud.create_line(0, HUD-1, WIDTH, HUD-1, fill=DIM_GREEN)