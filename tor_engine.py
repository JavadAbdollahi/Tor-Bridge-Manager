# tor_engine.py
# Manages a single Tor process: start, stop, bootstrap with cancel & timeout

import os
import sys
import subprocess
import time
import re
import msvcrt
from config import TOR_DIR, DATA_DIR_NAME, LOG_FILE, SERVER_NAME
from utils import draw_progress_bar, set_cmd_title

class TorEngine:
    def __init__(self):
        self.process = None
        self.is_running = False

    def get_paths(self):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        tor_exe = os.path.join(base_dir, TOR_DIR, "tor.exe")
        data_path = os.path.join(base_dir, DATA_DIR_NAME)
        log_path = os.path.join(data_path, LOG_FILE)
        return tor_exe, data_path, log_path

    def create_config(self, bridge_line, port):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        tor_exe, data_path, log_path = self.get_paths()
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        # Try to remove log file if exists, but ignore permission errors
        try:
            if os.path.exists(log_path):
                os.remove(log_path)
        except (PermissionError, OSError):
            # File is locked by another process, continue anyway
            pass

        lyrebird = os.path.join(base_dir, TOR_DIR, "pluggable_transports", "lyrebird.exe")
        if not os.path.exists(lyrebird):
            lyrebird = os.path.join(base_dir, TOR_DIR, "pluggable_transports", "obfs4proxy.exe")

        config = f"""
SocksPort 0.0.0.0:{port}
DataDirectory {data_path}
UseBridges 1
ClientTransportPlugin obfs4 exec {lyrebird}
Bridge {bridge_line}
Log notice file {log_path}
"""
        with open("torrc_temp", "w") as f:
            f.write(config)
        return log_path

    def start(self, bridge_line, port):
        # Ensure any previous Tor process is fully stopped
        self.stop()
        
        if self.is_running:
            return "ALREADY_RUNNING"

        tor_exe, _, log_path = self.get_paths()
        if not os.path.exists(tor_exe):
            return f"ERROR: tor.exe missing at {tor_exe}"

        self.create_config(bridge_line, port)

        try:
            self.process = subprocess.Popen(
                [tor_exe, "-f", "torrc_temp"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            print(f"  \033[93mEstablishing Circuit... (Press 'C' to cancel)\033[0m")
            
            timeout_wait_log = 0
            while not os.path.exists(log_path):
                if self.process.poll() is not None:
                    return "ERROR: Tor process died before log creation."
                time.sleep(0.1)
                timeout_wait_log += 1
                if timeout_wait_log > 50:
                    return "ERROR: Log creation timeout"

            last_percent = 0
            last_progress_time = time.time()
            start_time = time.time()
            MAX_TOTAL_SEC = 90
            STUCK_SEC = 40

            print("")
            with open(log_path, 'r') as f:
                while True:
                    if time.time() - start_time > MAX_TOTAL_SEC:
                        self.stop()
                        return "TIMEOUT_TOTAL"
                    if time.time() - last_progress_time > STUCK_SEC:
                        self.stop()
                        return "TIMEOUT_STUCK"
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode().upper()
                        if key == 'C':
                            print(f"\n  \033[91mCancelled by user.\033[0m")
                            self.stop()
                            return "CANCELLED"

                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        if self.process.poll() is not None:
                            return "ERROR: Tor process died during bootstrap."
                        continue

                    match = re.search(r'Bootstrapped (\d+)%', line)
                    if match:
                        percent = int(match.group(1))
                        if percent != last_percent:
                            last_percent = percent
                            last_progress_time = time.time()
                            draw_progress_bar(percent)
                        if percent == 100:
                            print(f"\n  \033[92mDone! Connected.\033[0m")
                            self.is_running = True
                            set_cmd_title(f"Connected (Port {port}) - {SERVER_NAME}")
                            return "SUCCESS"
        except Exception as e:
            return str(e)

    def stop(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        self.is_running = False
        set_cmd_title("Disconnected")
        if os.path.exists("torrc_temp"):
            try:
                os.remove("torrc_temp")
            except:
                pass