# agent/fsm.py
import math
from planning.potentials import compute_force
from planning.astar import AStarPlanner

class AgentFSM:
    """
    FSM estilo Helios con awareness de roles + fallback A* + potenciales.
    Estados: SearchBall, ApproachBall, TakeShot, DefendGoal
    """

    def __init__(self, unum, role_manager):
        self.unum = unum
        self.role_manager = role_manager
        self.role_name = role_manager.get_role(unum)
        self.state = "SearchBall"
        self.astar = AStarPlanner(cell_size=2.0)  # Planificador A*
        self.waypoint_path = None
        self.waypoint_idx = 0

        # Distancias clave según rol
        if self.role_name == "Goalie":
            self.APPROACH_DIST = 5.0
            self.SHOOT_DIST = 0.5
        elif self.role_name in ["CenterBack", "SideBack"]:
            self.APPROACH_DIST = 3.5
            self.SHOOT_DIST = 10.0
        elif self.role_name == "Midfielder":
            self.APPROACH_DIST = 2.5
            self.SHOOT_DIST = 5.0
        else:  # Forward, CenterForward
            self.APPROACH_DIST = 2.0
            self.SHOOT_DIST = 1.5

    def step(self, obs):
        """
        Decide acción:
        - Potenciales para aproximación normal
        - A* si bloqueado por oponentes
        """
        action = {"turn": 0.0, "dash": 0.0, "kick": None}

        ball = obs.get("ball")
        opponents = obs.get("opponents", [])
        teammates = obs.get("teammates", [])
        self_pos = (obs["self"]["x"], obs["self"]["y"])

        # =================================
        # 1. Sin pelota visible -> SearchBall
        # =================================
        if ball is None:
            self.state = "SearchBall"
            self.waypoint_path = None
            action["turn"] = 30.0
            action["dash"] = 15.0
            return action

        ball_dist = ball.get("dist", 999.0)
        ball_dir = ball.get("dir", 0.0)

        # =================================
        # 2. Muy cerca -> TakeShot
        # =================================
        if ball_dist < self.SHOOT_DIST:
            self.state = "TakeShot"
            self.waypoint_path = None
            action["kick"] = (100.0, ball_dir)
            action["turn"] = 0.0
            action["dash"] = 0.0
            return action

        # =================================
        # 3. Defensa proactiva (Goalie / Backs)
        # =================================
        if self.role_name in ["Goalie", "CenterBack", "SideBack"]:
            self.state = "DefendGoal"
            # CORRECCIÓN: usar paréntesis para la tupla
            goal_x, goal_y = (52.5, 0.0) if self.role_name != "Goalie" else (-52.5, 0.0)
            dx = goal_x - self_pos[0]
            dy = goal_y - self_pos[1]
            dist_goal = math.hypot(dx, dy)
            angle_goal = math.degrees(math.atan2(dy, dx))
            if dist_goal > 1.0:
                action["turn"] = angle_goal
                action["dash"] = min(80, dist_goal * 20)
                return action


        # =================================
        # 4. Aproximación con A* si hay oponentes cercanos
        # =================================
        self.state = "ApproachBall"
        close_opponents = [opp for opp in opponents if opp.get("dist", 999) < 5.0]

        if len(close_opponents) >= 2 and self.waypoint_path is None:
            obstacles = [(opp["x"], opp["y"]) for opp in opponents]
            ball_world = (ball["x"], ball["y"])
            self.waypoint_path = self.astar.plan(
                start_world=self_pos,
                goal_world=ball_world,
                obstacles_world=obstacles
            )
            self.waypoint_idx = 0

        # Seguir ruta A* si existe
        if self.waypoint_path and len(self.waypoint_path) > 0:
            if self.waypoint_idx >= len(self.waypoint_path):
                self.waypoint_path = None
            else:
                wp_x, wp_y = self.waypoint_path[self.waypoint_idx]
                wp_dist = math.hypot(wp_x - self_pos[0], wp_y - self_pos[1])
                if wp_dist < 1.0:
                    self.waypoint_idx += 1
                else:
                    wp_angle = math.degrees(math.atan2(wp_y - self_pos[1], wp_x - self_pos[0]))
                    action["turn"] = wp_angle
                    action["dash"] = min(100, wp_dist * 20)
                    return action

        # =================================
        # 5. Por defecto -> Potenciales
        # =================================
        goal_pos = (52.5, 0.0)
        angle, power = compute_force(
            self.unum,
            self_pos,
            ball,
            opponents,
            teammates,
            goal_pos,
            self.role_manager
        )

        action["turn"] = angle
        action["dash"] = min(100, power)
        return action
