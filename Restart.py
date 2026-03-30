if k == "space":
    if self.state in ("idle", "dead", "won"):
        self.state = "running"
        self.new_game()
        self._step()