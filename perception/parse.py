import re
import math

def parse_see(raw_msg):
    """Parse (see time ...) — extrae pelota, jugadores, banderas"""
    result = {
        "time": None,
        "self": {"x": 0.0, "y": 0.0, "angle": 0.0, "stamina": None},
        "ball": None,
        "teammates": [],
        "opponents": [],
    }

    # Tiempo
    time_match = re.search(r'\(see\s+(\d+)', raw_msg)
    if time_match:
        result["time"] = int(time_match.group(1))

    # Buscar PELOTA: ((ball) dist dir ...)
    ball_pattern = r'\(\(ball\)\s+([\-\d\.]+)\s+([\-\d\.]+)'
    ball_match = re.search(ball_pattern, raw_msg)
    
    if ball_match:
        try:
            dist = float(ball_match.group(1))
            direction = float(ball_match.group(2))
            if dist >= 0:
                x_rel = dist * math.cos(math.radians(direction))
                y_rel = dist * math.sin(math.radians(direction))
                result["ball"] = {
                    "x": x_rel,
                    "y": y_rel,
                    "vx": 0.0,
                    "vy": 0.0,
                    "dist": dist,
                    "dir": direction,
                }
        except:
            pass

    # Jugadores: ((player Right/Left unum) dist dir ...)
    player_pattern = r'\(\(player\s+(Right|Left)\s+(\d+)\)\s+([\-\d\.]+)\s+([\-\d\.]+)'
    players = re.findall(player_pattern, raw_msg)
    
    for team, unum_str, dist_str, dir_str in players:
        try:
            unum = int(unum_str)
            dist = float(dist_str)
            direction = float(dir_str)
            if dist >= 0:
                x_rel = dist * math.cos(math.radians(direction))
                y_rel = dist * math.sin(math.radians(direction))
                
                player_obj = {
                    "unum": unum,
                    "x": x_rel,
                    "y": y_rel,
                    "dist": dist,
                    "dir": direction,
                }
                
                if team.lower() == 'right':
                    result["teammates"].append(player_obj)
                else:
                    result["opponents"].append(player_obj)
        except:
            pass

    return result