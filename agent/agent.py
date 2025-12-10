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
        self.world_model.self_side = side 
        self.role_manager = role_manager
        self.fsm = AgentFSM(unum, role_manager)
    
    def handle_message(self, msg):
        pass