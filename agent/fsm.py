import math
from planning.potentials import compute_force
from planning.astar import AStarPlanner
import agent.tactics as tactics 

class AgentFSM:
    def __init__(self, unum, role_manager):
        self.unum = unum
        self.role_manager = role_manager
        self.role_name = role_manager.get_role(unum)
        self.state = "Positioning"
        self.astar = AStarPlanner(cell_size=3.0)
        self.waypoint_path = None
        self.current_wm = None 

    # IMPORTANTE: Recibe world_model (objeto), no obs (diccionario)
    def step(self, world_model):
        self.current_wm = world_model
        play_mode = getattr(world_model, "play_mode", "before_kick_off")
        
        # --- 0. LÓGICA DE ÁRBITRO ---
        if play_mode.startswith("goal_"):
            return {"turn": 0.0, "dash": 0.0, "kick": None}
            
        if play_mode == "before_kick_off":
            return {"turn": 0.0, "dash": 0.0, "kick": None}

        # --- SAQUE DE CENTRO ---
        is_my_kickoff = (play_mode == f"kick_off_{world_model.self_side}")
        ball = world_model.ball
        
        if is_my_kickoff and ball and ball["dist"] < 0.7:
             print(f"Agent {self.unum}: KICKOFF! Aggressive Start.")
             action = {"turn": 0.0, "dash": 0.0, "kick": None}
             pass_cmd = tactics.get_best_pass(self.current_wm, self.unum)
             if pass_cmd: action["kick"] = pass_cmd
             else: action["kick"] = (100.0, 45.0)
             return action

        # --- JUEGO NORMAL ---
        opponents = world_model.players_opponents
        teammates = world_model.players_teammates
        stamina = getattr(world_model, "stamina", 8000)

        if self.role_name == "Goalie":
            return self.strategy_goalie(ball, opponents, teammates, stamina)
        else:
            return self.strategy_field_player(ball, opponents, teammates, stamina)

    def strategy_goalie(self, ball, opponents, teammates, stamina):
        action = {"turn": 0.0, "dash": 0.0, "kick": None}
        if not ball:
            action["turn"] = 45.0
            return action
        dist_ball = ball["dist"]
        if dist_ball < 2.0:
            action["kick"] = (100.0, 60.0)
            return action
        if dist_ball < 15.0:
            target = {"x": ball["x"], "y": ball["y"]} 
            angle, power = compute_force(self.unum, (0,0), target, opponents, teammates, self.role_manager)
            action["turn"] = angle
            action["dash"] = 100.0
            return action
        action["turn"] = ball["dir"]
        return action

    def strategy_field_player(self, ball, opponents, teammates, stamina):
        action = {"turn": 0.0, "dash": 0.0, "kick": None}
        if not ball:
            action["turn"] = 60.0
            return action
        ball_dist = ball["dist"]
        
        if ball_dist < 0.7:
            # POSESIÓN
            my_side = self.current_wm.self_side
            shoot_cmd = tactics.get_shoot_action(self.current_wm, my_side)
            if shoot_cmd:
                action["kick"] = shoot_cmd
                return action
            pass_cmd = tactics.get_best_pass(self.current_wm, self.unum)
            if pass_cmd:
                action["kick"] = pass_cmd
                return action
            # Dribble
            action["kick"] = (40.0, 0.0) 
            action["dash"] = 40.0        
            return action

        # PERSECUCIÓN
        chase_threshold = 30.0 
        if self.role_manager.should_defend(self.unum): chase_threshold = 20.0
            
        if ball_dist < chase_threshold:
            target = {"x": ball["x"], "y": ball["y"]}
            # Coordenadas relativas -> self_pos siempre es (0,0)
            angle, power = compute_force(self.unum, (0,0), target, opponents, teammates, self.role_manager)
            action["turn"] = angle
            action["dash"] = power
        else:
            action["turn"] = ball["dir"]
            
        return action