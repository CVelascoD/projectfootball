import json

class RoleManager:
    def __init__(self, conf_file):
        self.roles = {}
        self.positions = {}
        self.load_config(conf_file)
    
    def load_config(self, conf_file):
        with open(conf_file, 'r') as f:
            data = json.load(f)
        for role_entry in data.get("role", []):
            unum = role_entry["number"]
            self.roles[unum] = { "name": role_entry["name"], "side": role_entry["side"] }
        positions_data = data.get("data", [{}])[0]
        for key, pos in positions_data.items():
            if key.isdigit():
                self.positions[int(key)] = (float(pos["x"]), float(pos["y"]))
    
    def get_role(self, unum):
        return self.roles.get(unum, {}).get("name", "Midfielder")
    
    def get_initial_position(self, unum):
        return self.positions.get(unum, (0, 0))
    
    def should_defend(self, unum):
        role = self.get_role(unum)
        return role in ["Goalie", "CenterBack", "SideBack"]
    
    def should_attack(self, unum):
        role = self.get_role(unum)
        return role in ["Forward", "CenterForward", "Midfielder"]