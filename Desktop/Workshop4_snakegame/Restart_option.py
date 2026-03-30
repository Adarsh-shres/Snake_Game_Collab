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

