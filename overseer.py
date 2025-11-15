"""
The Overseer - ASA Automation Framework
© 2025 NullForge Systems™ 
All Rights Reserved.
"""

from utils.rcon_client import RCON_Client
from utils.logger import Logger
import json


def load_settings():
    #load config/settings.json values
    try:
        with open("config/settings.json", "r") as f:
            return json.load()
        
    except FileNotFoundError:
        raise FileNotFoundError("Missing settings.json in /config")
    
def main():
    log = Logger()
    log.write("***The Overseer Protocol is starting***")

    settings = load_settings()

    host = settings["host"]
    port = settings["port"]
    password = settings["password"]

    test_command = settings.get("test_command", "cheat broadcast Overseer Test Successful")

    log.write(f"Connecting to RCON at {host}:{port} ...")

    try:
        rcon = RCON_Client(host, port, password)
        rcon.connect()
        log.write("RCON connection SUCCESSFUL")
    except Exception as e:
        log.write(f"Connection Failed due to {e}")
        return
    #send a test ping command
    log.write(f"Sending test command {test_command}")
    response = rcon.send(test_command)
    log.write(f"Server Response: {response}")

    log.write("***Overseer Test Completed***")

    if __name__ == "__main__":
        main()