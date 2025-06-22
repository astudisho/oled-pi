import os
import time
import socket
import fcntl
import struct
import subprocess

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
# Consider a smaller font if you need more lines.
from luma.core import const
# from PIL import ImageFont


fontSize = 10

# font = ImageFont.truetype("path/to/my/font.ttf", fontSize)


# ----------------------------------------------------
# Configuration for your specific OLED (common for 128x32)
# The PiKVM Plus documentation confirms it's a 128x32 OLED.
# The I2C address is usually 0x3C or 0x3D. Try 0x3C first.
# You might need to adjust the I2C bus (usually 1 for modern Pis).
# ----------------------------------------------------
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Function to get IP address for a specific interface
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except (IOError, OSError):
        return None

# Function to get Wi-Fi SSID
def get_wifi_ssid():
    try:
        result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "N/A"

# Function to check internet connectivity
def check_internet_connectivity():
    try:
        # Ping a reliable public DNS server (Google's 8.8.8.8)
        subprocess.run(['ping', '-c', '1', '-W', '1', '8.8.8.8'], capture_output=True, check=True)
        return "Online"
    except subprocess.CalledProcessError:
        return "Offline"
    
    # Function to get IPv6 address for a specific interface
def get_ipv6_address(ifname):
    try:
        # Get global unicast IPv6 address (excluding link-local 'fe80:')
        # Example output: "inet6 2605:xx:yy:zz::123/64 scope global"
        result = subprocess.run(
            ['ip', '-6', 'addr', 'show', ifname],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if 'inet6' in line and 'scope global' in line and 'fe80:' not in line:
                # Extract the address part, e.g., '2605:xx:yy:zz::123/64'
                parts = line.split()
                if len(parts) > 1:
                    ipv6_with_prefix = parts[parts.index('inet6') + 1]
                    # Return only the address, remove the '/XX' prefix
                    return ipv6_with_prefix.split('/')[0]
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_millideg = int(f.read())
    return temp_millideg / 1000.0  # Convert to Celsius


# Main loop to update the display
while True:
    ip_eth0 = get_ip_address('eth0')
    ip_wlan0 = get_ip_address('wlan0')
    ssid = get_wifi_ssid()
    internet = check_internet_connectivity()
    ipv6_eth0 = get_ipv6_address('eth0')
    temp = get_cpu_temp()

    print("Temp: ",temp)

    with canvas(device) as draw:
        # Clear previous content (important for OLED)pyu
        draw.rectangle(device.bounding_box, outline="black", fill="black")

        y_offset = 0
        line_height = fontSize # Adjust based on font size

        # Line 1: Connectivity Status
        draw.text((0, y_offset), f"Net: {internet}", fill="white")
        y_offset += line_height

        # Line 2: Ethernet IP
        if ip_eth0:
            draw.text((0, y_offset), f"Eth: {ip_eth0}", fill="white")
            y_offset += line_height
        else:
            draw.text((0, y_offset), "Eth: Disconnected", fill="white")
            y_offset += line_height

        # Line 3: Wi-Fi IP/SSID (combine due to limited space)
        if ip_wlan0:
            draw.text((0, y_offset), f"Wif: {ip_wlan0}", fill="white")
            y_offset += line_height
            # If space allows, you could try to show SSID on a fourth line, or truncate
            # For 128x32, 3 lines is often max comfortable viewing
        else:
            draw.text((0, y_offset), "Wif: Disconnected", fill="white")            

        if ssid != "N/A":
            draw.text((0, y_offset), f"SSID: {ssid}", fill="white")
            y_offset += line_height

        if temp:
            draw.text((0, y_offset), f"Temp: {temp} °C", fill="white")
            y_offset += line_height

        
        

    time.sleep(5) # Update every 5 seconds