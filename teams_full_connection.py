#!/usr/bin/env python3
import socket
import time
import threading
import json
import os
import re

from agent import Player
from agent.state import WorldModel
from agent.fsm import AgentFSM
from perception.parse import parse_see
from agent.roles import RoleManager

# Estos valores serán sobrescritos por run_team.py
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000
NUM_PLAYERS = 11
TEAM_NAME = "Right"
CONF_FILE = "conf_file.conf"

INIT_RE = re.compile(r"\(init\s+([lrLR])\s+(\d+)", re.IGNORECASE)


# -------------------------
# LOAD POSITIONS
# -------------------------
def load_positions(conf_file):
    if not os.path.exists(conf_file):
        raise FileNotFoundError(f"No se encontró {conf_file}")
    with open(conf_file, "r") as f:
        data = json.load(f)
    positions = {}
    for i in range(1, NUM_PLAYERS + 1):
        entry = data["data"][0].get(str(i))
        if entry is None:
            raise KeyError(f"No hay posición para '{i}' en {conf_file}")
        positions[i] = (float(entry["x"]), float(entry["y"]))
    return positions

# -------------------------
# SAFE SEND
# -------------------------
def safe_send(sock, msg, host, port):
    try:
        if not msg.endswith("\n"):
            msg = msg + "\n"
        sock.sendto(msg.encode(), (host, port))
    except Exception as e:
        print(f"[safe_send] send error: {e}")

        
# -------------------------
# PLAYER THREAD
# -------------------------
def player_thread(idx, positions, host, port, role_manager):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    sock.settimeout(0.8)

    # -------- 1. INIT --------
    try:
        safe_send(sock, f"(init {TEAM_NAME})", host, port)
    except Exception as e:
        print(f"[{TEAM_NAME} #{idx}] Error enviando init: {e}")
        sock.close()
        return

    # -------- 2. WAIT INIT REPLY --------
    side = None
    unum = None
    init_buf = ""
    INIT_TIMEOUT = 4.0
    t0 = time.time()
    server_addr = (host, port)

    while time.time() - t0 < INIT_TIMEOUT:
        try:
            data, server_addr = sock.recvfrom(8192)
            msg = data.decode(errors="ignore")
            init_buf += msg
            m = INIT_RE.search(init_buf)
            if m:
                side = m.group(1).lower()
                unum = int(m.group(2))
                print(f"[{TEAM_NAME} #{idx}] INIT OK: side={side}, unum={unum}")
                break
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[{TEAM_NAME} #{idx}] init recv error: {e}")
            break

    if unum is None:
        print(f"[{TEAM_NAME} #{idx}] Init failed, closing.")
        sock.close()
        return

    # -------- 3. POSITIONING --------
    target_pos = positions.get(unum) or positions.get(idx)
    if target_pos:
        x, y = target_pos
        print(f"[{TEAM_NAME} #{idx}] Moving to ({x:.2f},{y:.2f})")
        for _ in range(6):
            safe_send(sock, f"(move {x:.2f} {y:.2f})", host, port)
            time.sleep(0.08)

    # -------- 4. CREATE PLAYER + FSM --------
    if role_manager is None:
        from agent.roles import RoleManager
        role_manager = RoleManager(CONF_FILE)
    
    player = Player(side, unum, role_manager)
    sock.settimeout(1.0)

    # -------- 5. MAIN LOOP --------
    while True:
        try:
            data, server_addr = sock.recvfrom(8192)
            msg = data.decode(errors="ignore")

            # Log preview
            preview = msg.strip().splitlines()[0] if msg.strip() else ""
            if preview:
                print(f"[{TEAM_NAME} #{idx}] <<< {preview[:80]}")

            # PROCESAR MENSAJE
            if msg.startswith("(see"):
                # Parser + FSM + enviar acciones
                try:
                    obs = parse_see(msg)
                    player.last_obs = obs
                    action = player.fsm.step(obs)
                    
                    # Generar y enviar comandos
                    cmds = []
                    if action.get("turn") != 0.0:
                        cmds.append(f"(turn {action['turn']:.1f})")
                    if action.get("dash") != 0.0:
                        cmds.append(f"(dash {action['dash']:.1f})")
                    if action.get("kick") is not None:
                        power, angle = action["kick"]
                        cmds.append(f"(kick {power:.1f} {angle:.1f})")
                    
                    if not cmds:
                        cmds = ["(turn 0)"]
                    
                    for cmd in cmds:
                        print(f"[{TEAM_NAME} #{idx}] >>> {cmd}")
                        sock.sendto((cmd + "\n").encode(), server_addr)
                        time.sleep(0.003)
                        
                except Exception as e:
                    print(f"[{TEAM_NAME} #{idx}] (see) error: {e}")
                    import traceback
                    traceback.print_exc()

            elif msg.startswith("(sense_body"):
                # Actualizar stamina si es necesario
                try:
                    stamina_match = re.search(r'\(stamina\s+([\d\.]+)\s+', msg)
                    if stamina_match and player.last_obs:
                        player.last_obs["self"]["stamina"] = float(stamina_match.group(1))
                except:
                    pass

        except:
            break

    sock.close()


# -------------------------
# MAIN
# -------------------------
def main():
    host = SERVER_HOST
    port = SERVER_PORT

    try:
        positions = load_positions(CONF_FILE)
    except Exception as e:
        print(f"[main] Error cargando posiciones desde {CONF_FILE}: {e}")
        positions = {}

    # CARGAR ROLES DESDE CONF
    try:
        role_manager = RoleManager(CONF_FILE)
        print("[main] Roles cargados desde conf_file.conf")
    except Exception as e:
        print(f"[main] Error cargando roles: {e}")
        role_manager = None

    threads = []
    for i in range(1, NUM_PLAYERS + 1):
        t = threading.Thread(
            target=player_thread,
            args=(i, positions, host, port, role_manager),  # ← AÑADE role_manager
            daemon=True
        )
        t.start()
        threads.append(t)
        time.sleep(0.05)

    print(f"[main] Lanzados {len(threads)} hilos, esperando Ctrl-C para finalizar.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("[main] Interrupción recibida, saliendo.")

if __name__ == "__main__":
    main()

