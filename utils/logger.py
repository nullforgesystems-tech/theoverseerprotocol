"""
The Overseer - ASA Automation Framework
© 2025 NullForge Systems™
All Rights Reserved.
"""
import datetime

class Logger:

    #simple logging utility for The Overseer Protocol
    #writes to console and to data/overseer.log

    def __init__(self, logfile="data/overseer.log",):
        self.logfile = logfile

    def write(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

        out = f"[{timestamp}] {message}"

        #save to log file
        try:
            with open(self.logfile, "a") as f:
                f.write(out + "\n")
        except FileNotFoundError:

            import os
            os.makedirs("data", exist_ok=True)
            with self.open(self.logfile, "a") as f:
                f.write(out, "\n")
                