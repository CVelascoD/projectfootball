import math

def get_shoot_action(world_model, my_side):
    my_side_char = (my_side or "r")[0].lower()
    target_goal_side = 'l' if my_side_char == 'r' else 'r'
    
    goal = None
    for g in world_model.goals:
        if g["side"] == target_goal_side:
            goal = g
            break
    if not goal:
        goal = world_model.last_goal_seen.get(target_goal_side)
    if not goal: return None 
        
    if goal["dist"] > 45.0: return None
        
    shoot_angle = goal["dir"]
    blocked = False
    for opp in world_model.players_opponents:
        if opp["dist"] < goal["dist"] and abs(opp["dir"] - shoot_angle) < 6.0:
            blocked = True
            break
    if blocked: return None
    return (100.0, shoot_angle)

def get_best_pass(world_model, my_unum):
    best_mate = None
    best_score = -999
    
    for mate in world_model.players_teammates:
        dist = mate["dist"]
        angle = mate["dir"]
        
        if dist < 2.0: continue
        if dist > 45.0: continue 
        
        score = 0
        blocked = False
        for opp in world_model.players_opponents:
            if opp["dist"] < dist and abs(opp["dir"] - angle) < 5.0:
                blocked = True
                break
        if blocked: score -= 500
        
        if abs(angle) < 45.0: score += 20 
        score += dist * 0.5 
        
        if score > best_score and not blocked:
            best_score = score
            best_mate = mate
    if best_mate:
        pass_power = min(100.0, 40.0 + (best_mate["dist"] * 2.0))
        return (pass_power, best_mate["dir"])
    return None