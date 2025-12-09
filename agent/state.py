from collections import deque

class WorldModel:
    """
    Memoria interna del jugador.
    Mantiene información reciente del entorno.
    """

    def __init__(self, max_history=5):
        # tiempo
        self.time = 0

        # info propia
        self.self_side = None
        self.self_unum = None
        self.stamina = None
        self.can_kick = False

        # objetos visibles
        self.ball = None
        self.flags = []
        self.goals = []
        self.lines = []

        self.players_teammates = []
        self.players_opponents = []

        # historial
        self.ball_history = deque(maxlen=max_history)
        self.player_history = deque(maxlen=max_history)

    # -----------------------------------------------
    # Actualización desde un (see ...)
    # -----------------------------------------------


    def update_from_see(self, parsed):
        """
        parsed viene de parse_see(), que devuelve:
          {
            "time": int,
            "ball": {"dist": float, "dir": float} | None,
            "players": [{team, num, dist, dir}, ...],
            "flags": [{id, dist, dir}, ...]
          }
        """

        # actualizar tiempo
        if "time" in parsed and parsed["time"] is not None:
            self.time = parsed["time"]

        # pelota
        self.ball = parsed.get("ball", None)

        # jugadores
        self.players_teammates = []
        self.players_opponents = []

        for p in parsed.get("players", []):
            if p["team"] == self.self_side:
                self.players_teammates.append(p)
            else:
                self.players_opponents.append(p)

        # flags
        self.flags = parsed.get("flags", [])




    # -----------------------------------------------
    # Actualización desde (sense_body ...)
    # -----------------------------------------------
    def update_from_sense_body(self, stamina=None, can_kick=False):
        if stamina is not None:
            self.stamina = stamina
        self.can_kick = can_kick

    # -----------------------------------------------
    # Utilidad: estimar dirección futura del balón
    # -----------------------------------------------
    def estimate_ball_motion(self):
        if len(self.ball_history) < 2:
            return None

        prev = self.ball_history[-2]
        curr = self.ball_history[-1]

        return {
            "dist_change": curr["dist_change"],
            "dir_change": curr["dir_change"]
        }


