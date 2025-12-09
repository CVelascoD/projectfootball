#!/usr/bin/env python3
# run_team.py
"""
Orquestador simple para ejecutar teams_full_connection.py desde la CLI,
sin modificar teams_full_connection.py. Sobrescribe las constantes globales
del módulo antes de ejecutar main().
"""

import argparse
import logging
import os
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Run the RCSS team (wrapper for teams_full_connection.py)")
    p.add_argument("--conf", "-c", default="conf_file.conf", help="Path al archivo de configuración (conf_file.conf)")
    p.add_argument("--host", "-H", default="127.0.0.1", help="Host del servidor RCSS")
    p.add_argument("--port", "-P", type=int, default=6000, help="Puerto del servidor RCSS")
    p.add_argument("--players", "-n", type=int, default=11, help="Número de jugadores a conectar")
    p.add_argument("--team", "-t", default="Right", help="Nombre del equipo (TEAM_NAME)")
    p.add_argument("--logdir", "-l", default="logs", help="Directorio para logs (se crea si no existe)")
    return p.parse_args()

def setup_logging(logdir):
    os.makedirs(logdir, exist_ok=True)
    logfile = os.path.join(logdir, "run_team.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(logfile), logging.StreamHandler(sys.stdout)]
    )
    logging.info("Logging inicializado. fichero=%s", logfile)

def main():
    args = parse_args()
    setup_logging(args.logdir)
    logging.info("run_team: conf=%s host=%s port=%s players=%d team=%s",
                 args.conf, args.host, args.port, args.players, args.team)

    # Importamos el módulo con el código que ya tienes
    try:
        import teams_full_connection
    except Exception as e:
        logging.exception("No se pudo importar teams_full_connection: %s", e)
        raise

    # Verificamos que existe el conf file antes de ejecutar
    if not os.path.exists(args.conf):
        logging.error("Archivo de configuración no encontrado: %s", args.conf)
        sys.exit(2)

    # Inyectamos los valores en las variables globales del módulo
    # (esto evita tener que modificar el archivo original)
    try:
        setattr(teams_full_connection, "CONF_FILE", args.conf)
        setattr(teams_full_connection, "SERVER_HOST", args.host)
        setattr(teams_full_connection, "SERVER_PORT", args.port)
        setattr(teams_full_connection, "NUM_PLAYERS", args.players)
        setattr(teams_full_connection, "TEAM_NAME", args.team)
        logging.info("Globals inyectados en teams_full_connection.")
    except Exception as e:
        logging.exception("Error al inyectar globals en teams_full_connection: %s", e)
        raise

    # Ejecutamos main() del módulo. El propio main captura KeyboardInterrupt.
    try:
        logging.info("Llamando a teams_full_connection.main() ...")
        teams_full_connection.main()
    except KeyboardInterrupt:
        logging.info("Interrupción por usuario (KeyboardInterrupt). Saliendo.")
    except Exception as e:
        logging.exception("Error durante la ejecución de teams_full_connection.main(): %s", e)
        raise
    finally:
        logging.info("run_team finalizado.")

if __name__ == "__main__":
    main()

