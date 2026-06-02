# Tor Bridge Manager Ultimate (V1.1.3) 🛡️

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

### ✨ New Features (Latest Update)

1. **Cancel Connection** – If Tor gets stuck at 50% (or any percentage), you can press `C` to cancel the connection immediately. No more frozen terminal!
2. **Mobile Device Support** – Share your Tor proxy with your phone (Telegram, V2Ray, etc.) on the same Wi-Fi network. The app displays your local IP address for easy configuration.
3. **QR Code for V2Ray / Shadowrocket** – Press `Q` to generate a QR code. Scan it with your phone (V2Box, Shadowrocket, etc.) and instantly get a configured SOCKS5 proxy pointing to your laptop.

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
3. Install dependencies: `pip install requests qrcode[pil]`
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

### 3. Connecting & Cancelling
1. Press **[C]** to Connect.
2. The program will initialize the Tor engine and display a real-time progress bar.
3. **If it gets stuck** (e.g., at 50% for too long), simply press `C` to cancel. You can then try another bridge or check your network.
4. Once you see the green message **"Done! Connected"**, the proxy is ready.

---

## 🔗 Integration Guide

### Option A: Local Apps (Same Computer)
Use this for Telegram Desktop, Chrome, etc. on the same PC where the tool is running.

**Proxy Address:** `127.0.0.1`
**Port:** `9050` (Default or whatever you configured)

#### 📱 Telegram Configuration
1. Open Telegram Desktop.
2. Go to **Settings > Data and Storage > Use Proxy**.
3. Click **Add Proxy**.
4. Select **SOCKS5**.
   * **Server:** `127.0.0.1`
   * **Port:** `9050`
5. Click Save.

#### 🌐 Browser Configuration (Chrome/Edge/Firefox)
Use **Proxy SwitchyOmega**:
1. Install [Proxy SwitchyOmega](https://chrome.google.com/webstore/detail/proxy-switchyomega/padekgcemlokbadohgkifijomclgjgif).
2. Open Options > **New Profile** > Name it "Tor".
3. Protocol: **SOCKS5**.
4. Server: `127.0.0.1` | Port: `9050`.
5. Click **Apply Changes**.
6. Select "Tor" from the extension popup.

### Option B: Mobile Devices (Same Wi-Fi) – New!
The tool now displays your **Local IP** (e.g., `192.168.1.5`) in the main menu. Use this to connect your phone to the same Tor proxy.

#### 📱 Telegram on Android / iPhone
1. Make sure your phone is connected to the **same Wi-Fi** as your laptop.
2. Go to Telegram Settings → Data and Storage → Use Proxy.
3. Add a **SOCKS5** proxy:
   - Server: `192.168.x.x` (the IP shown in the tool)
   - Port: `9050`
4. Save and enable.

#### 📱 V2Box / Shadowrocket (for V2Ray)
1. In the Tor Manager, press `Q` to generate a QR code.
2. Open V2Box (or Shadowrocket) on your phone.
3. Tap "Scan QR Code" and scan the code displayed on your laptop.
4. A new server named "Bita" (or your chosen name) will appear. Connect to it.
5. You are now using your laptop's Tor connection on your phone!

---

## 🐞 Bug Fixes & Improvements (Recent Changelog)

- **Fixed `PermissionError` on `bootstrap.log`** – The app no longer crashes if the log file is locked by a previous Tor process.
- **Removed global `taskkill`** – Stopping Tor now only terminates the specific process, avoiding accidental killing of other Tor instances.
- **Fixed Windows `title` command error** – The console title no longer causes `'Connected' is not recognized` errors.
- **Improved GeoIP reliability** – Added fallback APIs (`ipapi.co`, `ipwho.is`) and a cache to reduce rate‑limiting issues.
- **Added connection timeout & stuck detection** – Automatically aborts the connection after 90 seconds total or 40 seconds without progress.
- **Cleaner temporary file handling** – `torrc_temp` is removed automatically after disconnection.

---

## 🧠 Technical Concepts (Educational)

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