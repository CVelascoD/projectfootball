import re
import math

def parse_see(raw_msg):
    result = { "time": None, "ball": None, "teammates": [], "opponents": [], "goals": [] }
    time_match = re.search(r'\(see\s+(\d+)', raw_msg)
    if time_match: result["time"] = int(time_match.group(1))
    
    ball_match = re.search(r'\(\(ball\)\s+([\-\d\.]+)\s+([\-\d\.]+)', raw_msg)
    if ball_match:
        dist = float(ball_match.group(1))
        direction = float(ball_match.group(2))
        result["ball"] = { "dist": dist, "dir": direction, "x": dist * math.cos(math.radians(direction)), "y": dist * math.sin(math.radians(direction)) }

    player_iter = re.finditer(r'\(\(player\s+([a-zA-Z0-9_]+)\s+(\d+)\)\s+([\-\d\.]+)\s+([\-\d\.]+)', raw_msg)
    for m in player_iter:
        player = { "team": m.group(1), "unum": int(m.group(2)), "dist": float(m.group(3)), "dir": float(m.group(4)) }
        player["x"] = player["dist"] * math.cos(math.radians(player["dir"]))
        player["y"] = player["dist"] * math.sin(math.radians(player["dir"]))
        result["teammates"].append(player) 

    goal_iter = re.finditer(r'\(\(g\s+([lr])\)\s+([\-\d\.]+)\s+([\-\d\.]+)', raw_msg)
    for m in goal_iter:
        result["goals"].append({ "side": m.group(1), "dist": float(m.group(2)), "dir": float(m.group(3)) })
    return result