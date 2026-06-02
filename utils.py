# utils.py
# Helper functions: screen clear, title, geoip, ping, progress bar, local IP

import os
import sys
import time
import socket
import base64
from geo_service import GeoLocationService
from config import APP_TITLE, SERVER_NAME


# Global instance of geo service (can be reused across calls)
_geo_service = GeoLocationService(cache_ttl=3600)

# utils.py - replace the get_geoip function with this

def get_geoip(ip):
    """
    Get country name for an IP using multiple free APIs with fallback.
    Results are cached in memory.
    """
    # Simple cache attached to the function itself
    if not hasattr(get_geoip, "cache"):
        get_geoip.cache = {}
    
    # Return from cache if available
    if ip in get_geoip.cache:
        return get_geoip.cache[ip]
    
    # List of APIs to try (in order of preference)
    apis = [
        ("ip-api.com", f"http://ip-api.com/json/{ip}", lambda d: d.get('country', d.get('countryCode', 'Unknown'))),
        ("ipapi.co", f"https://ipapi.co/{ip}/json/", lambda d: d.get('country_name', 'Unknown')),
        ("ipwho.is", f"http://ipwho.is/{ip}", lambda d: d.get('country', 'Unknown')),
    ]
    
    for name, url, extractor in apis:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                country = extractor(data)
                if country and country != "Unknown":
                    # Store in cache
                    get_geoip.cache[ip] = country
                    return country
        except Exception as e:
            # Silently ignore errors and try next API
            continue
    
    # If all APIs fail
    return "Unknown"

def clear_screen():
    """Clear terminal screen (Windows/Linux)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def set_cmd_title(status="Idle"):
    """Set console window title (Windows only) - fixed quoting issue"""
    if os.name == 'nt':
        # Remove pipe and ampersand which cause command chaining
        safe_status = status.replace('|', '-').replace('&', '-')
        # Build full title string
        title_str = f"{APP_TITLE} - {SERVER_NAME} - {safe_status}"
        # Use double quotes to handle spaces and parentheses
        os.system(f'title "{title_str}"')


def get_local_ip():
    """Get local IPv4 address (e.g., 192.168.x.x)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip.startswith("127."):
                return "127.0.0.1 (loopback)"
            return ip
        except:
            return "Unavailable"

def get_geoip(ip):
    """Get country code for an IP using ip-api.com"""
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
    """Measure TCP connection latency in milliseconds"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    start = time.time()
    try:
        s.connect((ip, int(port)))
        s.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

def draw_progress_bar(percent, width=40, color_start='\033[94m', color_end='\033[0m'):
    """Display a simple progress bar"""
    filled = int(width * percent // 100)
    bar = '█' * filled + '-' * (width - filled)
    sys.stdout.write(f"\r  {color_start}[{bar}] {percent}%{color_end}")
    sys.stdout.flush()
    
def generate_shadowsocks_config(server_ip, server_port):
    """
    Generate a Shadowsocks URL (ss://) with a remark (fragment) for server name.
    The fragment '#Bita' will be displayed as the server name in compatible apps.
    """
    import base64
    method = "chacha20-ietf-poly1305"
    password = "tor-bridge-manager"
    # Encode method:password as base64
    user_info = f"{method}:{password}"
    encoded_user_info = base64.b64encode(user_info.encode()).decode()
    # Build URL with fragment #Bita
    config_url = f"ss://{encoded_user_info}@{server_ip}:{server_port}#Bita"
    return config_url

def generate_socks5_config(server_ip, server_port):
    """
    Generate a simple SOCKS5 proxy URL for QR code.
    """
    userpass_host = f":@{server_ip}:{server_port}"
    encoded = base64.b64encode(userpass_host.encode()).decode()
    return f"socks://{encoded}#{SERVER_NAME}"

