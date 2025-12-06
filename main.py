import os
import sys
import json
import subprocess
import time
import socket
import threading
import re
from datetime import datetime

# ================= CONFIGURATION =================
GITHUB_LINK = "github.com/JavadAbdollahi"
APP_TITLE = "Tor Bridge Manager Ultimate"
DATA_FILE = "data.json"
TOR_DIR = "tor"
DATA_DIR_NAME = "tor_data"
LOG_FILE = "bootstrap.log"
DEFAULT_PORT = 9050

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# ================= UTILS =================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_cmd_title(status="Idle"):
    if os.name == 'nt':
        os.system(f"title {APP_TITLE} | Status: {status}")

def get_geoip(ip):
    try:
        import requests
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("country", data.get("countryCode", "Unknown"))
    except:
        return "Unknown"
    return "Unknown"

def tcp_ping(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    start = time.time()
    try:
        s.connect((ip, int(port)))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def draw_progress_bar(percent, width=40):
    filled = int(width * percent // 100)
    bar = '█' * filled + '-' * (width - filled)
    sys.stdout.write(f"\r  {Colors.BLUE}[{bar}] {percent}%{Colors.ENDC}")
    sys.stdout.flush()

# ================= DATA MANAGER =================
class DataManager:
    def __init__(self):
        self.data = {
            "servers": [],
            "selected_index": -1,
            "port": DEFAULT_PORT
        }
        self.load()

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.data = json.load(f)
            except: pass

    def save(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_server(self, line, ip, port, location):
        for s in self.data["servers"]:
            if s['ip'] == ip and s['port'] == port:
                return False
        self.data["servers"].append({
            "line": line,
            "ip": ip,
            "port": port,
            "location": location,
            "ping": 9999,
            "added_at": datetime.now().strftime("%Y-%m-%d")
        })
        if len(self.data["servers"]) == 1:
            self.data["selected_index"] = 0
        self.save()
        return True

    def delete_server(self, index):
        if 0 <= index < len(self.data["servers"]):
            del self.data["servers"][index]
            if self.data["selected_index"] >= index:
                self.data["selected_index"] = max(-1, self.data["selected_index"] - 1)
            self.save()

    def clear_all_servers(self):
        self.data["servers"] = []
        self.data["selected_index"] = -1
        self.save()

# ================= TOR ENGINE =================
class TorEngine:
    def __init__(self):
        self.process = None
        self.is_running = False

    def get_paths(self):
        # FIX: Robust path detection for both EXE and Python Script
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        tor_exe = os.path.join(base_dir, TOR_DIR, "tor.exe")
        data_path = os.path.join(base_dir, DATA_DIR_NAME)
        log_path = os.path.join(data_path, LOG_FILE)
        
        return tor_exe, data_path, log_path

    def create_config(self, bridge_line, port):
        # Use base_dir to find pluggable transports correctly
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        tor_exe, data_path, log_path = self.get_paths()
        
        if not os.path.exists(data_path): os.makedirs(data_path)
        if os.path.exists(log_path):
            try: os.remove(log_path)
            except: pass

        lyrebird = os.path.join(base_dir, TOR_DIR, "pluggable_transports", "lyrebird.exe")
        if not os.path.exists(lyrebird):
            lyrebird = os.path.join(base_dir, TOR_DIR, "pluggable_transports", "obfs4proxy.exe")

        config = f"""
SocksPort {port}
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
        if self.is_running: return "ALREADY_RUNNING"
        tor_exe, _, log_path = self.get_paths()
        
        if not os.path.exists(tor_exe): return "ERROR: tor.exe missing at " + tor_exe

        self.create_config(bridge_line, port)
        
        try:
            self.process = subprocess.Popen(
                [tor_exe, "-f", "torrc_temp"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            
            print(f"  {Colors.WARNING}Establishing Circuit... (If stuck at 50%, try another bridge){Colors.ENDC}")
            success = False
            timeout = 0
            while not os.path.exists(log_path):
                time.sleep(0.1)
                timeout += 1
                if timeout > 50: return "ERROR: Log creation failed"

            with open(log_path, 'r') as f:
                last_percent = 0
                stuck_counter = 0
                
                while True:
                    if self.process.poll() is not None:
                        return "ERROR: Tor process died."
                    
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        # Check if stuck
                        if last_percent == 50:
                            stuck_counter += 1
                            if stuck_counter > 300: # 30 seconds stuck warning
                                sys.stdout.write(f"\r  {Colors.FAIL}[!] Slow connection... be patient...{Colors.ENDC}")
                        continue
                    
                    match = re.search(r'Bootstrapped (\d+)%', line)
                    if match:
                        percent = int(match.group(1))
                        last_percent = percent
                        draw_progress_bar(percent)
                        if percent == 100:
                            print(f"\n  {Colors.GREEN}Done! Connected.{Colors.ENDC}")
                            success = True
                            break
            
            if success:
                self.is_running = True
                set_cmd_title(f"Connected (Port {port})")
                return "SUCCESS"
            else:
                self.stop()
                return "FAILED"
        except Exception as e:
            return str(e)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None
        subprocess.call("taskkill /IM tor.exe /F", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.is_running = False
        set_cmd_title("Disconnected")

# ================= UI & APP =================
class App:
    def __init__(self):
        self.db = DataManager()
        self.tor = TorEngine()

    def refresh_pings_and_sort(self):
        if not self.db.data["servers"]: return
        print(f"\n  {Colors.WARNING}Auto-updating server status...{Colors.ENDC}")
        threads = []
        for s in self.db.data["servers"]:
            t = threading.Thread(target=lambda x: x.update({'ping': tcp_ping(x['ip'], x['port'])}), args=(s,))
            t.start()
            threads.append(t)
        for t in threads: t.join()
        self.db.data["servers"].sort(key=lambda x: x.get('ping', 9999))
        self.db.data["selected_index"] = 0
        self.db.save()

    def print_header(self):
        clear_screen()
        print(f"{Colors.CYAN}")
        print(r"""
 ________                           ______                                                       __     
|        \                         /      \                                                     |  \    
 \$$$$$$$$______    ______        |  $$$$$$\  ______   _______   _______    ______    _______  _| $$_   
   | $$  /      \  /      \       | $$   \$$ /      \ |       \ |       \  /      \  /       \|   $$ \  
   | $$ |  $$$$$$\|  $$$$$$\      | $$      |  $$$$$$\| $$$$$$$\| $$$$$$$\|  $$$$$$\|  $$$$$$$ \$$$$$$  
   | $$ | $$  | $$| $$   \$$      | $$   __ | $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$    $$| $$        
   | $$ | $$__/ $$| $$            | $$__/  \| $$__/ $$| $$  | $$| $$  | $$| $$$$$$$$| $$_____   | $$|  \
   | $$  \$$    $$| $$             \$$    $$ \$$    $$| $$  | $$| $$  | $$ \$$     \ \$$     \   \$$  $$
    \$$   \$$$$$$  \$$              \$$$$$$   \$$$$$$  \$$   \$$ \$$   \$$  \$$$$$$$  \$$$$$$$    \$$$$ 
        """)
        print(f"{Colors.ENDC}")
        print(f"{Colors.HEADER}  >> GitHub: {GITHUB_LINK} <<{Colors.ENDC}")
        print("  " + "="*60)
        status = f"{Colors.GREEN}CONNECTED{Colors.ENDC}" if self.tor.is_running else f"{Colors.FAIL}DISCONNECTED{Colors.ENDC}"
        print(f"  STATUS: {status} | PORT: {Colors.WARNING}{self.db.data['port']}{Colors.ENDC}")
        print("  " + "="*60 + "\n")

    def print_servers(self):
        if not self.db.data["servers"]:
            print(f"  {Colors.WARNING}No servers available. Add bridges to start.{Colors.ENDC}")
            return
        print(f"  {'NO':<4} {'LOCATION':<15} {'IP ADDRESS':<20} {'PING':<10} {'STATUS'}")
        print(f"  {'-'*60}")
        for idx, s in enumerate(self.db.data["servers"]):
            marker = f"{Colors.GREEN}<SELECTED>{Colors.ENDC}" if idx == self.db.data["selected_index"] else ""
            ping_val = s.get('ping', 9999)
            p_color = Colors.GREEN if ping_val < 200 else (Colors.WARNING if ping_val < 500 else Colors.FAIL)
            ping_str = f"{ping_val}ms" if ping_val != 9999 else "Down"
            loc = (s['location'][:13] + '..') if len(s['location']) > 15 else s['location']
            print(f"  {idx+1:<4} {loc:<15} {s['ip']:<20} {p_color}{ping_str:<10}{Colors.ENDC} {marker}")
        print("\n")

    def menu(self):
        print(f"  [{Colors.CYAN}A{Colors.ENDC}] Add Server      [{Colors.CYAN}S{Colors.ENDC}] Select Server")
        print(f"  [{Colors.CYAN}D{Colors.ENDC}] Delete Server   [{Colors.CYAN}P{Colors.ENDC}] Port Config")
        print(f"  [{Colors.CYAN}R{Colors.ENDC}] Reload Ping     [{Colors.CYAN}C{Colors.ENDC}] Connect/Disconnect")
        print(f"  [{Colors.FAIL}Q{Colors.ENDC}] Quit")
        print(f"  {'-'*60}")

    def run(self):
        self.tor.stop()
        while True:
            self.print_header()
            self.print_servers()
            self.menu()
            choice = input("  Command > ").strip().upper()

            if choice == 'A':
                # --- NEW INSTRUCTION SECTION ---
                print(f"\n  {Colors.CYAN}--- Where to get bridges? ---{Colors.ENDC}")
                print(f"  1. Telegram Bot: {Colors.BOLD}@GetBridgesBot{Colors.ENDC}")
                print(f"  2. Website: {Colors.BOLD}https://bridges.torproject.org/options{Colors.ENDC}")
                print(f"  {Colors.BLUE}Now paste your bridge lines below (Press Enter twice to finish):{Colors.ENDC}")
                
                lines = []
                while True:
                    try:
                        line = input()
                        if not line: break
                        lines.append(line)
                    except: break
                
                full_text = "\n".join(lines)
                matches = re.findall(r'(obfs4.*?)(\n|$)', full_text)
                if matches:
                    print("  Processing...")
                    count = 0
                    for m in matches:
                        bridge_line = m[0].strip()
                        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+):(\d+)', bridge_line)
                        if ip_match:
                            ip, port = ip_match.group(1), ip_match.group(2)
                            print(f"  > Found {ip}...", end=" ", flush=True)
                            loc = get_geoip(ip)
                            if self.db.add_server(bridge_line, ip, port, loc):
                                print(f"{Colors.GREEN}Added ({loc}){Colors.ENDC}")
                                count += 1
                            else:
                                print(f"{Colors.WARNING}Duplicate{Colors.ENDC}")
                    if count > 0: self.refresh_pings_and_sort()
                    else: input("  No new valid servers found. Press Enter...")
                else: input("  No 'obfs4' lines detected. Press Enter...")

            elif choice == 'S':
                try:
                    idx = int(input("  Server NO: ")) - 1
                    if 0 <= idx < len(self.db.data["servers"]):
                        self.db.data["selected_index"] = idx
                        self.db.save()
                except: pass

            elif choice == 'D':
                try:
                    val = input("  Server NO to delete (0 to Delete ALL): ")
                    idx = int(val)
                    if idx == 0:
                        confirm = input(f"  {Colors.FAIL}Are you sure you want to delete ALL servers? (y/n): {Colors.ENDC}")
                        if confirm.lower() == 'y':
                            self.db.clear_all_servers()
                    else:
                        self.db.delete_server(idx - 1)
                        self.refresh_pings_and_sort()
                except: pass

            elif choice == 'C':
                if self.tor.is_running:
                    self.tor.stop()
                else:
                    if not self.db.data["servers"]: continue
                    idx = self.db.data["selected_index"]
                    if idx == -1 and self.db.data["servers"]: idx = 0
                    srv = self.db.data["servers"][idx]
                    res = self.tor.start(srv['line'], self.db.data['port'])
                    if res != "SUCCESS": input(f"\n  {Colors.FAIL}Error: {res}{Colors.ENDC}")
                    else: time.sleep(1)

            elif choice == 'R': self.refresh_pings_and_sort()
            elif choice == 'P':
                try:
                    self.db.data['port'] = int(input(f"  New Port: "))
                    self.db.save()
                except: pass
            elif choice == 'Q':
                self.tor.stop()
                sys.exit()

if __name__ == "__main__":
    try: App().run()
    except KeyboardInterrupt: pass