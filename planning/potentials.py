import math
FIELD_X_MIN, FIELD_X_MAX = -52.5, 52.5
FIELD_Y_MIN, FIELD_Y_MAX = -34.0, 34.0

def compute_force(self_unum, self_pos, target, opponents, teammates, role_manager):
    x, y = self_pos 
    f_x, f_y = 0.0, 0.0
    if target:
        dx, dy = target["x"] - x, target["y"] - y
        dist_t = math.hypot(dx, dy)
        force_strength = 150.0 
        if dist_t > 0.5:
            f_x += (dx / dist_t) * force_strength
            f_y += (dy / dist_t) * force_strength
    for opp in opponents:
        dist_o = math.hypot(opp["x"], opp["y"])
        if dist_o < 0.1: dist_o = 0.1
        if opp.get("dist", 999) < 4.0:
            rep = min(120.0, 40.0 / (dist_o**2))
            f_x -= (opp["x"] / dist_o) * rep
            f_y -= (opp["y"] / dist_o) * rep
    for mate in teammates:
        dist_m = math.hypot(mate["x"], mate["y"])
        if dist_m < 0.1: dist_m = 0.1
        if mate.get("dist", 999) < 3.0:
            rep = min(80.0, 20.0 / (dist_m**2))
            f_x -= (mate["x"] / dist_m) * rep
            f_y -= (mate["y"] / dist_m) * rep
    
    force_mag = math.hypot(f_x, f_y)
    if force_mag < 0.5: return 0.0, 0.0 
    return math.degrees(math.atan2(f_y, f_x)), min(100.0, force_mag)