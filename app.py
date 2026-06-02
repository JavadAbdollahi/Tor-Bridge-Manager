# app.py
# Main application UI, menus, and user interaction (single connection with QR code)

import threading
import time
import re
import sys
import os
import qrcode
from config import Colors, GITHUB_LINK, SERVER_NAME, TELEGRAM_LINK
from utils import (
    clear_screen, tcp_ping, get_geoip, get_local_ip,
    draw_progress_bar, generate_socks5_config
)
from data_manager import DataManager
from tor_engine import TorEngine

class App:
    def __init__(self):
        self.db = DataManager()
        self.tor = TorEngine()

    def refresh_pings_and_sort(self):
        """Update ping times for all bridges in parallel and sort by latency"""
        if not self.db.data["servers"]:
            return
        print(f"\n  {Colors.WARNING}Auto-updating server status...{Colors.ENDC}")
        threads = []
        for s in self.db.data["servers"]:
            t = threading.Thread(target=lambda x: x.update({'ping': tcp_ping(x['ip'], x['port'])}), args=(s,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        self.db.data["servers"].sort(key=lambda x: x.get('ping', 9999))
        # keep selected index at first after sort
        self.db.data["selected_index"] = 0
        self.db.save()

    def print_header(self):
        """Display ASCII banner, status, port and local IP"""
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
        print(f"{Colors.HEADER}  >> Telegram: {TELEGRAM_LINK} <<{Colors.ENDC}")
        print("  " + "="*60)

        # Status line with server name "Bita"
        status_text = f"{Colors.GREEN}CONNECTED to {SERVER_NAME}{Colors.ENDC}" if self.tor.is_running else f"{Colors.FAIL}DISCONNECTED{Colors.ENDC}"
        print(f"  STATUS: {status_text} | PORT: {Colors.WARNING}{self.db.data['port']}{Colors.ENDC}")

        local_ip = get_local_ip()
        print(f"  LOCAL IP (for same network): {Colors.CYAN}{local_ip}{Colors.ENDC}")
        print("  " + "="*60 + "\n")

    def print_servers(self):
        """List all bridges with location, IP, ping and selection marker"""
        if not self.db.data["servers"]:
            print(f"  {Colors.WARNING}No bridges available. Use 'A' to add.{Colors.ENDC}")
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
        """Display interactive menu"""
        print(f"  [{Colors.CYAN}A{Colors.ENDC}] Add Bridge     [{Colors.CYAN}S{Colors.ENDC}] Select Bridge")
        print(f"  [{Colors.CYAN}D{Colors.ENDC}] Delete Bridge  [{Colors.CYAN}P{Colors.ENDC}] Port Config")
        print(f"  [{Colors.CYAN}R{Colors.ENDC}] Refresh Pings  [{Colors.CYAN}C{Colors.ENDC}] Connect/Disconnect")
        print(f"  [{Colors.CYAN}Q{Colors.ENDC}] Show QR Code   [{Colors.FAIL}E{Colors.ENDC}] Exit")
        print(f"  {'-'*60}")

    def show_qr_code(self):
        """Generate and display QR code for current Tor SOCKS proxy (with server name 'Bita')"""
        if not self.tor.is_running:
            input(f"  {Colors.WARNING}Please establish a connection first (press 'C').{Colors.ENDC}")
            return

        local_ip = get_local_ip()
        port = self.db.data['port']
        # Generate Shadowsocks URL with fragment "#Bita" as server name
        config_link = generate_socks5_config(local_ip, port)    # instead of generate_shadowsocks_config

        # Create QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(config_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        print(f"\n  {Colors.CYAN}📱 QR Code for {SERVER_NAME} (SOCKS5 proxy on {local_ip}:{port}){Colors.ENDC}")
        print(f"  URL: {config_link}")
        print("  Opening image... scan it with your phone (Shadowrocket, V2Box, etc.)")

        # Save and open image
        qr_path = "tor_qr.png"
        img.save(qr_path)
        os.system(f"start {qr_path}")   # Windows
        input("\n  Press Enter after scanning to close...")
        try:
            os.remove(qr_path)
        except:
            pass

    def run(self):
        """Main application loop"""
        self.tor.stop()   # ensure clean state
        while True:
            self.print_header()
            self.print_servers()
            self.menu()
            choice = input("  Command > ").strip().upper()

            if choice == 'A':
                # --- Add bridge from user input ---
                print(f"\n  {Colors.CYAN}--- Where to get bridges? ---{Colors.ENDC}")
                print(f"  1. Telegram Bot: {Colors.BOLD}@GetBridgesBot{Colors.ENDC}")
                print(f"  2. Website: {Colors.BOLD}https://bridges.torproject.org/options{Colors.ENDC}")
                print(f"  3. Email: {Colors.BOLD}bridges@torproject.org{Colors.ENDC}")
                print(f"  {Colors.BLUE}Paste bridge lines (press Enter twice to finish):{Colors.ENDC}")
                lines = []
                while True:
                    line = input()
                    if not line:
                        break
                    lines.append(line)
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
                    if count > 0:
                        self.refresh_pings_and_sort()
                    else:
                        input("  No new bridges added. Press Enter...")
                else:
                    input("  No 'obfs4' lines found. Press Enter...")

            elif choice == 'S':
                # Select a bridge by number
                try:
                    idx = int(input("  Bridge number to select: ")) - 1
                    if 0 <= idx < len(self.db.data["servers"]):
                        self.db.data["selected_index"] = idx
                        self.db.save()
                    else:
                        print("  Invalid number.")
                except:
                    pass

            elif choice == 'D':
                # Delete bridge(s)
                if not self.db.data["servers"]:
                    continue
                try:
                    val = input("  Bridge number to delete (0 = delete ALL): ")
                    idx = int(val)
                    if idx == 0:
                        confirm = input(f"  {Colors.FAIL}Delete ALL bridges? (y/n): {Colors.ENDC}")
                        if confirm.lower() == 'y':
                            self.db.clear_all_servers()
                    else:
                        self.db.delete_server(idx - 1)
                        self.refresh_pings_and_sort()
                except:
                    pass

            elif choice == 'C':
                # Connect / Disconnect Tor
                if self.tor.is_running:
                    self.tor.stop()
                else:
                    if not self.db.data["servers"]:
                        input("  No bridges available. Add one first. Press Enter...")
                        continue
                    idx = self.db.data["selected_index"]
                    if idx == -1 and self.db.data["servers"]:
                        idx = 0
                    srv = self.db.data["servers"][idx]
                    res = self.tor.start(srv['line'], self.db.data['port'])
                    if res == "SUCCESS":
                        time.sleep(1)
                    elif res == "CANCELLED":
                        input(f"\n  {Colors.WARNING}Connection cancelled. Press Enter...{Colors.ENDC}")
                    elif res.startswith("TIMEOUT"):
                        input(f"\n  {Colors.FAIL}Connection timeout. Press Enter...{Colors.ENDC}")
                    elif res != "SUCCESS":
                        input(f"\n  {Colors.FAIL}Error: {res}{Colors.ENDC}")

            elif choice == 'R':
                # Refresh ping times
                self.refresh_pings_and_sort()

            elif choice == 'P':
                # Change SOCKS port
                try:
                    new_port = int(input(f"  Enter new SOCKS port (current: {self.db.data['port']}): "))
                    self.db.data['port'] = new_port
                    self.db.save()
                    print(f"  Port changed to {new_port}. Restart connection if needed.")
                    time.sleep(1)
                except:
                    pass

            elif choice == 'Q':
                # Show QR code
                self.show_qr_code()

            elif choice == 'E':
                # Exit
                self.tor.stop()
                sys.exit(0)