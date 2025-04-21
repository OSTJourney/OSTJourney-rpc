# OSTJourney-RPC

## Description:
This repository provides a standalone **Discord Rich Presence (RPC)** client for OSTJourney. It displays your current music playing status directly on your Discord profile using local client-side scripts.

### Key Features:
- Displays the currently playing song from OSTJourney on Discord.
- Updates automatically when the track changes.
- Lightweight and cross-platform compatible (Windows, Linux, MacOS).
- Fully decoupled from the main website logic — works independently.

---

## **Requirements**

Before you begin, make sure you have the following installed:

- **Python** (3.8+)
- **Pip**
- **Virtualenv** (recommended)
- **Discord RPC running locally** (the Discord desktop app must be open)

---

## **Installation**

### 1. **Clone the Repository**
```bash
git clone https://github.com/OSTJourney/OSTJourney-rpc.git
cd rpc
```

### 3. **Create and Activate a Virtual Environment**
**Linux/macOS**
```bash
python -m venv venv
source venv/bin/activate
```
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```
### 3. Install the Required Dependencies
```bash
pip install -r requirements.txt
```

## **Configuration**
You can set up a `.env` file to configure the behavior of the script. Example:
```ini
RPC_CLIENT_ID="your_discord_app_id"
WEB_SOCKET_PORT="web socket port (default 4242)"
IMG_DOMAIN="https://ostjourney.xyz or your website"
```
You can register your own Discord Application [here](https://discord.com/developers) and get your client ID.

## **Usage**
Run the RPC client:
```bash
python main.py
```
Once running, the script will start pushing the currently playing track to your Discord Rich Presence (if the site is open and playing a song).
**Warning** The script must be running before the website is loaded !

## **License**
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/OSTJourney/rpc/blob/main/LICENSE)

## **Contributing**

Pull requests, feedback, and forks are welcome. Feel free to open an issue or suggest enhancements!