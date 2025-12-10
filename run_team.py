#!/usr/bin/env python3
import argparse
import logging
import os
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Run Soccer-IA Team")
    p.add_argument("--conf", "-c", default="conf_file.conf", help="Path al config")
    p.add_argument("--host", "-H", default="127.0.0.1", help="Host RCSS")
    p.add_argument("--port", "-P", type=int, default=6000, help="Puerto RCSS")
    p.add_argument("--players", "-n", type=int, default=11, help="Num jugadores")
    p.add_argument("--team", "-t", default="SoccerIA", help="Nombre del equipo")
    p.add_argument("--logdir", "-l", default="logs", help="Dir logs")
    return p.parse_args()

def setup_logging(logdir):
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, "run_team.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)]
    )

def main():
    args = parse_args()
    setup_logging(args.logdir)
    logging.info(f"Iniciando {args.team}...")

    try:
        import teams_full_connection
    except Exception as e:
        logging.exception(f"Error importando teams_full_connection: {e}")
        raise

    if not os.path.exists(args.conf):
        logging.error(f"Config no encontrada: {args.conf}")
        sys.exit(2)

    try:
        setattr(teams_full_connection, "CONF_FILE", args.conf)
        setattr(teams_full_connection, "SERVER_HOST", args.host)
        setattr(teams_full_connection, "SERVER_PORT", args.port)
        setattr(teams_full_connection, "NUM_PLAYERS", args.players)
        setattr(teams_full_connection, "TEAM_NAME", args.team)
    except Exception as e:
        logging.exception(f"Error inyectando globals: {e}")
        raise

    try:
        teams_full_connection.main()
    except KeyboardInterrupt:
        logging.info("Interrupción por usuario.")
    except Exception as e:
        logging.exception(f"Error en main loop: {e}")
    finally:
        logging.info("Finalizado.")

if __name__ == "__main__":
    main()