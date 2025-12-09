import json

class RoleManager:
    """Gestiona roles, posiciones iniciales y comportamientos por rol"""
    
    def __init__(self, conf_file):
        self.roles = {}
        self.positions = {}
        self.load_config(conf_file)
    
    def load_config(self, conf_file):
        with open(conf_file, 'r') as f:
            data = json.load(f)
        
        # Mapear roles por unum
        for role_entry in data.get("role", []):
            unum = role_entry["number"]
            self.roles[unum] = {
                "name": role_entry["name"],
                "side": role_entry["side"],  # C, L, R
            }
        
        # Mapear posiciones iniciales
        positions_data = data.get("data", [{}])[0]
        for key, pos in positions_data.items():
            if key.isdigit():
                unum = int(key)
                self.positions[unum] = (float(pos["x"]), float(pos["y"]))
    
    def get_role(self, unum):
        """Retorna nombre del rol (Goalie, Forward, Midfielder, etc.)"""
        return self.roles.get(unum, {}).get("name", "Midfielder")
    
    def get_initial_position(self, unum):
        """Retorna posición inicial (x, y)"""
        return self.positions.get(unum, (0, 0))
    
    def should_defend(self, unum):
        """¿Este jugador debe defender? (Goalie, Backs, Center)"""
        role = self.get_role(unum)
        return role in ["Goalie", "CenterBack", "SideBack"]
    
    def should_attack(self, unum):
        """¿Este jugador debe atacar? (Forwards, Midfielders)"""
        role = self.get_role(unum)
        return role in ["Forward", "CenterForward", "Midfielder"]
    
    def get_formation_zone(self, unum):
        """Retorna zona defensiva/ofensiva recomendada (x, y)"""
        return self.get_initial_position(unum)