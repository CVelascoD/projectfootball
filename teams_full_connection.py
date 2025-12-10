#!/usr/bin/env python3
import socket
import time
import threading
import json
import os
import re
import traceback

from agent import Player
from agent.state import WorldModel
from agent.fsm import AgentFSM
from perception.parse import parse_see
from agent.roles import RoleManager
from agent.logger import GameLogger 

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000
NUM_PLAYERS = 11
TEAM_NAME = "Right"
CONF_FILE = "conf_file.conf"

INIT_RE = re.compile(r"\(init\s+([lrLR])\s+(\d+)", re.IGNORECASE)

def load_positions(conf_file):
    if not os.path.exists(conf_file):
        raise FileNotFoundError(f"No se encontró {conf_file}")
    with open(conf_file, "r") as f:
        data = json.load(f)
    positions = {}
    for i in range(1, NUM_PLAYERS + 1):
        entry = data["data"][0].get(str(i))
        if entry is None:
            positions[i] = (0.0, 0.0) 
        else:
            positions[i] = (float(entry["x"]), float(entry["y"]))
    return positions

def safe_send(sock, msg, host, port):
    try:
        if not msg.endswith("\n"):
            msg = msg + "\n"
        sock.sendto(msg.encode(), (host, port))
    except Exception as e:
        print(f"[safe_send] send error: {e}")


def player_thread(idx, positions, host, port, role_manager):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    sock.settimeout(0.8)

    try:
        safe_send(sock, f"(init {TEAM_NAME})", host, port)
    except Exception as e:
        print(f"[{TEAM_NAME} #{idx}] Error enviando init: {e}")
        sock.close()
        return

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

    target_pos = positions.get(unum) or positions.get(idx)
    if target_pos:
        x, y = target_pos
        print(f"[{TEAM_NAME} #{idx}] Moving to ({x:.2f},{y:.2f})")
        for _ in range(6):
            safe_send(sock, f"(move {x:.2f} {y:.2f})", host, port)
            time.sleep(0.08)

    if role_manager is None:
        role_manager = RoleManager(CONF_FILE)
    
    player = Player(side, unum, role_manager)
    
    player.world_model.self_role = role_manager.get_role(unum)
    
    logger = GameLogger(TEAM_NAME, unum)

    sock.settimeout(1.0)

    while True:
        try:
            data, server_addr = sock.recvfrom(8192)
            msg = data.decode(errors="ignore")

            if msg.startswith("(see"):
                try:
                    obs_dict = parse_see(msg)
                    player.world_model.update_from_see(obs_dict)
                    
                    action = player.fsm.step(player.world_model)
                    
                    logger.log_tick(player.world_model, action)
                    
                    cmds = []
                    turn_val = action.get("turn", 0.0)
                    dash_val = action.get("dash", 0.0)
                    kick_val = action.get("kick")
                    
                    if turn_val != 0.0:
                        cmds.append(f"(turn {turn_val:.1f})")
                    if dash_val != 0.0:
                        cmds.append(f"(dash {dash_val:.1f})")
                    if kick_val is not None:
                        power, angle = kick_val
                        cmds.append(f"(kick {power:.1f} {angle:.1f})")
                    
                    if not cmds:
                        cmds = ["(turn 0)"]
                    
                    for cmd in cmds:
                        safe_send(sock, cmd, host, port)
                        time.sleep(0.003)
                        
                except Exception as e:
                    print(f"[{TEAM_NAME} #{idx}] (see) error: {e}")
                    traceback.print_exc()

            elif msg.startswith("(hear"):
                try:
                    if "referee" in msg:
                        m = re.search(r'\(hear\s+\d+\s+referee\s+([a-zA-Z0-9_]+)\)', msg)
                        if m:
                            mode = m.group(1)
                            player.world_model.play_mode = mode
                except Exception as e:
                    pass

            elif msg.startswith("(sense_body"):
                try:
                    stamina_match = re.search(r'\(stamina\s+([\d\.]+)\s+', msg)
                    if stamina_match:
                        stamina = float(stamina_match.group(1))
                        player.world_model.update_from_sense_body(stamina=stamina)
                except:
                    pass

        except Exception as e:
            break

    logger.close()
    sock.close()

def main():
    host = SERVER_HOST
    port = SERVER_PORT

    try:
        positions = load_positions(CONF_FILE)
    except Exception as e:
        print(f"[main] Error cargando posiciones desde {CONF_FILE}: {e}")
        positions = {}

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
            args=(i, positions, host, port, role_manager),
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