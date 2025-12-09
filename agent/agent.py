# agent/agent.py
import re
from agent.state import WorldModel
from agent.fsm import AgentFSM
from agent.roles import RoleManager
from perception.parse import parse_see

class Player:
    def __init__(self, side, unum, role_manager):
        self.side = side
        self.unum = unum
        self.world_model = WorldModel()
        self.role_manager = role_manager
        self.fsm = AgentFSM(unum, role_manager)
        self.server_params = None
        self.last_obs = None
    
    def handle_message(self, msg):
        """Actualizar con see o sense_body"""
        if msg.startswith("(see"):
            obs = parse_see(msg)
            self.last_obs = obs
        elif msg.startswith("(sense_body"):
            stamina_match = re.search(r'\(stamina\s+([\d\.]+)\s+', msg)
            if stamina_match and self.last_obs:
                self.last_obs["self"]["stamina"] = float(stamina_match.group(1))
    
    def decide_and_act(self):
        """FSM -> comandos"""
        if self.last_obs is None:
            return ["(turn 0)"]
        
        action = self.fsm.step(self.last_obs)
        commands = []
        
        if action.get("turn") != 0.0:
            commands.append(f"(turn {action['turn']:.1f})")
        if action.get("dash") != 0.0:
            commands.append(f"(dash {action['dash']:.1f})")
        if action.get("kick") is not None:
            power, angle = action["kick"]
            commands.append(f"(kick {power:.1f} {angle:.1f})")
        
        if not commands:
            commands.append("(turn 0)")
        
        return commands