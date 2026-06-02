# data_manager.py
# Manages storage of bridges (JSON file)

import json
import os
from datetime import datetime

class DataManager:
    def __init__(self, data_file="data.json"):
        self.data_file = data_file
        self.data = {
            "servers": [],
            "selected_index": -1,
            "port": 9050
        }
        self.load()

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except:
                pass

    def save(self):
        with open(self.data_file, 'w') as f:
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