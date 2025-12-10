import numpy as np

class FeatureExtractor:
    def __init__(self):
        self.obs_size = 49 

    def get_observation(self, world_model):
        obs = []
        if world_model.ball:
            obs.extend([min(world_model.ball["dist"] / 60.0, 1.0), world_model.ball["dir"] / 180.0])
        else: 
            obs.extend([-1.0, 0.0])

        obs.append(getattr(world_model, "stamina", 8000) / 8000.0)
        
        goals_data = {g["side"]: g for g in world_model.goals}
        for side in ['l', 'r']:
            g = goals_data.get(side)
            obs.extend([g["dist"] / 120.0, g["dir"] / 180.0] if g else [-1.0, 0.0])

        teammates = sorted(world_model.players_teammates, key=lambda x: x["dist"])
        for i in range(10):
            p = teammates[i] if i < len(teammates) else None
            obs.extend([p["dist"] / 60.0, p["dir"] / 180.0] if p else [-1.0, 0.0])

        opponents = sorted(world_model.players_opponents, key=lambda x: x["dist"])
        for i in range(11):
            p = opponents[i] if i < len(opponents) else None
            obs.extend([p["dist"] / 60.0, p["dir"] / 180.0] if p else [-1.0, 0.0])

        return np.array(obs, dtype=np.float32)