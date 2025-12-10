import math
import os
import torch
import numpy as np

from planning.potentials import compute_force
from planning.astar import AStarPlanner
import agent.tactics as tactics 

from training.models import Actor
from training.features import FeatureExtractor

class AgentFSM:
    def __init__(self, unum, role_manager):
        self.unum = unum
        self.role_manager = role_manager
        self.role_name = role_manager.get_role(unum)
        self.state = "Positioning"
        self.astar = AStarPlanner(cell_size=3.0)
        self.waypoint_path = None
        self.current_wm = None 
        self.use_neural = False
        self.actor = None
        self.feature_extractor = FeatureExtractor()
        self.model_path = "models/actor_v1.pth"
        
        if self.role_name != "Goalie" and os.path.exists(self.model_path):
            try:
                self.actor = Actor(obs_size=49)
                self.actor.load_state_dict(torch.load(self.model_path, map_location="cpu"))
                self.actor.eval()
                self.use_neural = True
            except Exception as e:
                print(f"Agent {unum}: Error cargando cerebro: {e}")

    def step(self, world_model):
        self.current_wm = world_model
        play_mode = getattr(world_model, "play_mode", "before_kick_off")
        
        if play_mode.startswith("goal_"):
            return {"turn": 0.0, "dash": 0.0, "kick": None}
        if play_mode == "before_kick_off":
            return {"turn": 0.0, "dash": 0.0, "kick": None}

        if self.role_name == "Goalie":
            return self.strategy_goalie(world_model.ball, world_model.players_opponents, world_model.players_teammates)

        if self.use_neural:
            return self.strategy_neural(world_model)
            
        return self.strategy_field_player_classic(world_model)

    def strategy_neural(self, world_model):
        try:
            obs_np = self.feature_extractor.get_observation(world_model)
            obs_tensor = torch.FloatTensor(obs_np).unsqueeze(0) 
            
            with torch.no_grad():
                p_dash, p_turn, p_kick_prob, p_kick_pow, p_kick_ang = self.actor(obs_tensor)
            
            action = {"turn": 0.0, "dash": 0.0, "kick": None}
            
            dash_val = p_dash.item() * 100.0
            turn_val = p_turn.item() * 180.0
            
            if dash_val > 5.0: action["dash"] = dash_val
            if abs(turn_val) > 5.0: action["turn"] = turn_val
            
            if p_kick_prob.item() > 0.5:
                k_pow = p_kick_pow.item() * 100.0
                k_ang = p_kick_ang.item() * 180.0
                action["kick"] = (k_pow, k_ang)
            
            return action
            
        except Exception as e:
            print(f"Neural Error: {e}")
            return self.strategy_field_player_classic(world_model)

    def strategy_field_player_classic(self, world_model):
        ball = world_model.ball
        opponents = world_model.players_opponents
        teammates = world_model.players_teammates
        
        action = {"turn": 0.0, "dash": 0.0, "kick": None}
        if not ball:
            action["turn"] = 60.0
            return action
        
        ball_dist = ball["dist"]
        
        if ball_dist < 0.7:
            shoot = tactics.get_shoot_action(world_model, world_model.self_side)
            if shoot: 
                action["kick"] = shoot
                return action
            pazz = tactics.get_best_pass(world_model, self.unum)
            if pazz: 
                action["kick"] = pazz
                return action
            action["kick"] = (40.0, 0.0)
            return action

        chase_thr = 30.0 if not self.role_manager.should_defend(self.unum) else 20.0
        if ball_dist < chase_thr:
            target = {"x": ball["x"], "y": ball["y"]}
            angle, power = compute_force(self.unum, (0,0), target, opponents, teammates, self.role_manager)
            action["turn"] = angle
            action["dash"] = power
        else:
            action["turn"] = ball["dir"]
            
        return action

    def strategy_goalie(self, ball, opponents, teammates):
        action = {"turn": 0.0, "dash": 0.0, "kick": None}
        if not ball:
            action["turn"] = 45.0
            return action
        if ball["dist"] < 2.0:
            action["kick"] = (100.0, 60.0)
            return action
        if ball["dist"] < 15.0:
            target = {"x": ball["x"], "y": ball["y"]} 
            angle, power = compute_force(self.unum, (0,0), target, opponents, teammates, self.role_manager)
            action["turn"] = angle
            action["dash"] = 100.0
            return action
        action["turn"] = ball["dir"]
        return action