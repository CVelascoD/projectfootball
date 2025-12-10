from collections import deque

class WorldModel:
    def __init__(self, max_history=5):
        self.time = 0
        self.play_mode = "before_kick_off"
        self.self_side = None
        self.self_unum = None
        self.self_role = "Unknown"
        self.stamina = 8000
        self.ball = None
        self.goals = [] 
        self.last_goal_seen = {"l": None, "r": None} 
        self.players_teammates = []
        self.players_opponents = []
        self.ball_history = deque(maxlen=max_history)

    def update_from_see(self, parsed):
        if "time" in parsed and parsed["time"] is not None:
            self.time = parsed["time"]
        self.ball = parsed.get("ball")
        current_goals = parsed.get("goals", [])
        self.goals = current_goals
        for g in current_goals:
            self.last_goal_seen[g["side"]] = g
        self.players_teammates = []
        self.players_opponents = []
        raw_players = parsed.get("teammates", []) + parsed.get("opponents", [])
        for p in raw_players:
            p_team = p.get("team", "")
            if self.self_side and p_team.lower() == self.self_side.lower():
                self.players_teammates.append(p)
            else:
                self.players_opponents.append(p)

    def update_from_sense_body(self, stamina=None, can_kick=False):
        if stamina is not None:
            self.stamina = stamina