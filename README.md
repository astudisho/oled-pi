# OLED Network Status Display for Raspberry Pi

This Python script displays real-time network information on a 128x32 SSD1306 OLED screen connected via I2C. It shows Ethernet and Wi-Fi IP addresses, SSID, and internet connectivity status.

## 🛠️ Features

- Displays:
  - Ethernet IP address
  - Wi-Fi IP address and SSID
  - Internet connectivity (via ping)
  - Optional: Global IPv6 address
- Auto-refreshes every 5 seconds
- Designed for 128x32 OLED using the `luma.oled` library
* **Ethernet (eth0) IP Address (IPv4)**: Shows the current IPv4 address of the wired connection.
* **WiFi (wlan0) IP Address (IPv4)**: Displays the current IPv4 address of the wireless connection.
* **WiFi SSID**: Shows the name of the connected WiFi network.
* **Internet Connectivity Status**: Pings a public DNS server to determine if the device is "Online" or "Offline".
* **IPv6 Addresses**: Fetches global unicast IPv6 addresses for both `eth0` and `wlan0` (currently logged to `journalctl` due to screen space, but ready for display implementation).
* **Automatic Refresh**: Updates the display every 5 seconds.
* **Systemd Service**: Configured to run reliably in the background and start automatically on boot.


## 📦 Requirements

- Raspberry Pi with I2C enabled
- SSD1306 OLED display (128x32)
- Python 3
- Dependencies:
  ```bash
  pip install luma.oled

## Setup Instructions

Follow these steps to set up and run the display script on your Raspberry Pi.

### 1. Create Project Directory

```bash
mkdir -p ~/Documents/Programacion/Python/Screen
cd ~/Documents/Programacion/Python/Screen
```

### 2. Create and Activate Virtual Environment
It's highly recommended to use a Python virtual environment to manage dependencies.

Bash

python3 -m venv .venv
source .venv/bin/activate

### 3. Install Python Dependencies
With your virtual environment active, install the necessary libraries:

Bash

```bash
pip install luma.oled smbus2 Pillow
```

### 5. Create the Systemd Service File
This allows the script to run automatically in the background and start on boot.

Create a file named oled_info.service in /etc/systemd/system/:

```
sudo nano /etc/systemd/system/oled_info.service
```

### 6. Enable and Start the Service
After saving both screen.py and oled_info.service, run these commands to make the service active:

Bash

sudo systemctl daemon-reload   # Reload systemd to recognize the new service file
sudo systemctl enable oled_info.service # Enable the service to start on boot
sudo systemctl start oled_info.service # Start the service immediately

### 7. Check Service Status and Logs
To verify if the service is running correctly and to see any debug output or errors, use:

Bash

sudo systemctl status oled_info.service
journalctl -u oled_info.service -f
The journalctl -f command will show you the real-time output from your script, including the DEBUG: lines, which are invaluable for troubleshooting.