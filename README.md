# Tor Bridge Manager Ultimate (V1.0)🛡️

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**Tor Bridge Manager** is a lightweight, CLI-based tool designed to help users in restricted network environments manage, test, and connect to Tor Bridges efficiently. It acts as a wrapper around the Tor Expert Bundle, providing a user-friendly interface to manage multiple bridges, sort them by speed (TCP Ping), and connect seamlessly.

---

## 🚀 Features

- **Bridge Management:** Add, delete, and organize `obfs4` bridges easily.
- **Auto-Location:** Automatically detects the country of the bridge server.
- **Smart Sorting:** Pings all saved bridges and sorts them by lowest latency.
- **Visual Feedback:** Real-time progress bar during the connection bootstrap process.
- **Port Configuration:** Custom SOCKS5 port selection (Default: 9050).
- **Persistent Data:** Remembers your servers and settings automatically.

---

## 🛠️ Installation (No Python Required)

This program is **Portable**. You do not need to install Python, drivers, or any other software.

### ✅ The Easy Way (Recommended)
1. Go to the **[Releases]** page on the right side of this repository.
2. Download the latest `.zip` file (e.g., `TorManager_v2.0.zip`).
3. **Extract** the zip file to a folder on your computer.
4. Run `TorManager.exe`.

*That's it! The folder already contains the necessary Tor engine files.*

---

### 🤓 The Developer Way (Source Code)
Only use this method if you want to modify the code or run it via Python.
1. Clone this repository.
2. Install Python 3.8+.
3. Install dependencies: `pip install requests`
4. Download the Tor Expert Bundle and place it in the `tor` folder.
5. Run `python main.py`.

## 📖 How to Use

### 1. Getting Bridges
To bypass censorship, you need "Bridges". You can obtain them from official sources:
* **Telegram:** [@GetBridgesBot](https://t.me/GetBridgesBot)
* **Website:** [Tor Project Bridges](https://bridges.torproject.org/options)
* **Email:** bridges@torproject.org

### 2. Adding Bridges to the App
1. Run `TorManager.exe` (or `python main.py`).
2. Press **[A]** to select "Add Server".
3. Paste your bridge lines. You can paste multiple lines at once (e.g., the entire message from the Telegram bot).
4. Press **Enter** twice.
5. The program will automatically validate the bridges, fetch their geo-location, and save them to your list.

### 3. Connecting
1. Press **[C]** to Connect.
2. The program will initialize the Tor engine and display a real-time progress bar.
3. Once you see the green message **"Done! Connected"**, the proxy is ready, minimize the window (do not close it).


---

## 🔗 Integration Guide

### Option A: Specific Apps (Recommended)
Use this if you only want Telegram or a specific browser to tunnel through Tor.
you can manually configure specific applications to use Tor.
**Proxy Address:** `127.0.0.1`
**Port:** `9050` (Default or whatever you configured)

### 📱 Telegram Configuration
1. Open Telegram Desktop.
2. Go to **Settings > Data and Storage > Use Proxy**.
3. Click **Add Proxy**.
4. Select **SOCKS5**.
   * **Server:** `127.0.0.1`
   * **Port:** `9050`
5. Click Save. The shield icon should appear with a checkmark.

### 🌐 Browser Configuration (Chrome/Edge/Firefox)
For the best experience, use a proxy management extension like **SwitchyOmega**:
1. Install [Proxy SwitchyOmega](https://chrome.google.com/webstore/detail/proxy-switchyomega/padekgcemlokbadohgkifijomclgjgif).
2. Open Options > **New Profile** > Name it "Tor".
3. Protocol: **SOCKS5**.
4. Server: `127.0.0.1` | Port: `9050`.
5. Click **Apply Changes**.
6. Click the extension icon in your browser toolbar and select "Tor".

### Option B: Route System-Wide Traffic (Manual)
Use this if you want **ALL** applications (Windows updates, games, browsers) to use Tor.

1. Open Windows Start Menu and search for **"Proxy Settings"**.
2. Under "Manual proxy setup", turn **Use a proxy server** to **ON**.
3. IP Address: `127.0.0.1`
4. Port: `9050`
5. Click **Save**.

*Note: Remember to turn this OFF when you close the Tor Manager, otherwise you won't have internet access.*

---

## 🧠 Technical Concepts (Educational)

Here is a brief explanation of the underlying technologies used in this project:

### 1. What is a Port (9050)?
Think of your computer's IP address as a "House" and Ports as "Doors".
* Normal websites usually enter through Door 80 or 443.
* This program opens a special internal door (**9050**) inside your house. When you configure Telegram to use this port, you are essentially telling it: *"Do not go out through the main door; go through door 9050 where the Tor software is waiting to encrypt your data."*

### 2. What is TCP Ping?
Standard "Ping" uses the ICMP protocol. However, many censorship-resistant servers block ICMP packets, making them appear "dead" even if they are working.
* This tool uses **TCP Ping**. It attempts to perform a TCP Handshake (SYN packet) with the specific port of the bridge.
* It measures the time taken for the server to acknowledge the request (SYN-ACK). This provides a much more accurate metric for service availability and latency in restricted networks.

### 3. What is `obfs4`?
Standard Tor traffic has a distinct fingerprint that firewalls can easily recognize and block.
* **obfs4** (The Pluggable Transport used in this tool) acts as a camouflage layer. It scrambles the Tor traffic to look like random, unidentifiable data bytes. To a Deep Packet Inspection (DPI) firewall, the traffic appears as random noise, allowing it to pass through.

---

## ⚠️ Disclaimer
This tool is open-source software designed for educational purposes and personal privacy protection. It is provided "as is", without warranty of any kind. Please use this tool responsibly and ensure you comply with the laws and regulations of your region regarding the use of encryption and anonymity software.