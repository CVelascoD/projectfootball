import math

def compute_force(self_unum, self_pos, target, opponents, teammates, goal_pos, role_manager):
    """
    Calcula fuerza resultante usando potenciales.
    target = {"x", "y", "dist", "dir"} → puede ser pelota o posición de apoyo
    """
    x, y = self_pos
    role = role_manager.get_role(self_unum)
    
    f_x, f_y = 0.0, 0.0

    # Atracción al objetivo
    if target and target.get("dist", 999) < 60:
        t_x, t_y = target["x"], target["y"]
        dist_t = math.hypot(t_x, t_y)
        if dist_t > 0.5:
            # Intensidad por rol
            if role in ["Forward", "CenterForward"]:
                force_strength = 100.0
            elif role == "Midfielder":
                force_strength = 60.0
            elif role in ["CenterBack", "SideBack"]:
                force_strength = 40.0
            else:
                force_strength = 20.0
            f_x += (t_x / dist_t) * force_strength
            f_y += (t_y / dist_t) * force_strength

    # Repulsión de oponentes
    for opp in opponents:
        opp_dist = opp.get("dist", 999)
        if opp_dist < 10:
            o_x, o_y = opp["x"], opp["y"]
            dist_o = math.hypot(o_x, o_y)
            if dist_o > 0.5:
                repulsion_mag = (10 - dist_o) * 8
                f_x -= (o_x / dist_o) * repulsion_mag
                f_y -= (o_y / dist_o) * repulsion_mag

    # Atracción débil a portería para atacantes
    if role in ["Forward", "CenterForward"] and target.get("dist", 999) < 60:
        goal_x, goal_y = goal_pos
        dist_goal = math.hypot(goal_x, goal_y)
        if dist_goal > 1.0:
            f_x += (goal_x / dist_goal) * 10.0
            f_y += (goal_y / dist_goal) * 10.0

    # Composición final
    force_mag = math.hypot(f_x, f_y)
    if force_mag < 0.5:
        angle_deg = 0.0
        power = 0.0
    else:
        angle_rad = math.atan2(f_y, f_x)
        angle_deg = angle_rad * 180.0 / math.pi
        power = min(100.0, force_mag * 0.8)

    return angle_deg, power
