import json
import time
import os

class GameLogger:
    def __init__(self, team_name, unum, log_dir="logs"):
        self.team_name = team_name
        self.unum = unum
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        timestamp = int(time.time())
        self.filename = f"{log_dir}/{team_name}_{unum}_{timestamp}.jsonl"
        self.file = open(self.filename, "w")
        
    def log_tick(self, world_model, action):
        entry = {
            "time": world_model.time,
            "play_mode": getattr(world_model, "play_mode", "unknown"),
            "stamina": getattr(world_model, "stamina", 0),
            "role": getattr(world_model, "self_role", "unknown"),
            "ball": world_model.ball, 
            "action": action
        }
        json_str = json.dumps(entry)
        self.file.write(json_str + "\n")
        self.file.flush()

    def close(self):
        if self.file: self.file.close()