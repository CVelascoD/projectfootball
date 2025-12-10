class RewardCalculator:
    def __init__(self, team_side):
        self.team_side = team_side 
        self.enemy_goal_side = 'l' if team_side == 'r' else 'r'
    def calculate(self, current_wm, prev_wm, action):
        reward = 0.0
        curr_dist, prev_dist = self._get_goal_dist(current_wm), self._get_goal_dist(prev_wm)
        if curr_dist and prev_dist: reward += (prev_dist - curr_dist) * 1.0 
        if action.get("kick"): reward += 0.2 
        reward -= (abs(action.get("dash", 0.0)) / 100.0) * 0.01
        return reward
    def _get_goal_dist(self, wm):
        for g in wm.goals:
            if g["side"] == self.enemy_goal_side: return g["dist"]
        mem_goal = wm.last_goal_seen.get(self.enemy_goal_side)
        return mem_goal["dist"] if mem_goal else None