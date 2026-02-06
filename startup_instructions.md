# Raspberry Pi: Systemd Service & WiFi Configuration Setup

This guide outlines how to create a systemd service (so a program runs at boot) and how to configure WiFi using wpa_supplicant. Paths and names are generalized; replace placeholders with your own values.

---

## Part 1: WiFi Configuration

1. **Edit the WiFi config file:**

   ```bash
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   ```

2. **Add or adjust the following** (replace placeholders with your network details):

   ```
   country=CA
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1

   network={
       ssid="YOUR_WIFI_SSID"
       psk="YOUR_WIFI_PASSWORD"
       key_mgmt=WPA-PSK
   }
   ```

3. **Useful commands:**
   - Check WiFi interface details: `iwconfig wlan0`
   - Check WiFi service status: `sudo systemctl status wpa_supplicant.service`

---

## Part 2: Systemd Service (run a program at boot)

1. **Create your service file** (use a descriptive name, e.g. `my-app.service`):

   ```bash
   sudo nano /etc/systemd/system/<service-name>.service
   ```

2. **Paste a unit file like this** (replace all placeholders) (If not using USB):

   ```ini
   [Unit]
   Description=start AI speech-to-speech application on boot
   After=network-online.target #Ensures that the program doesn't run unless a wifi connection is established

   [Service]
   User=<your_username>
   WorkingDirectory=/home/<your_username>/<project_directory>
   ExecStart=/home/<your_username>/<venv_path>/bin/python3 gpio_speech_main.py
   Restart=always #Retries every 5 seconds in the case of failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target #Ensures boot is still complete even if this fails
   ```

2.1 **Paste a unit file like this (replace all placeholders) (If using USB):** 

'''ini[Unit]
Description=Audio Test Script
After=pulseaudio.service sound.target
# Wait for the system service to trigger USB audio
After=usb-audio-trigger.service

[Service]
Type=simple
Environment=XDG_RUNTIME_DIR=/run/user/<your_user_id>
# Trigger udev with sudo (passwordless via sudoers file)
ExecStartPre=/usr/bin/sudo /usr/bin/udevadm trigger --subsystem-match=sound --action=add
ExecStartPre=/usr/bin/sudo /usr/bin/udevadm settle
ExecStartPre=/bin/sleep 2
ExecStart=/home/<your_username>/main_files/speech_start.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
'''

2.5 **Create the file for sudo permissions (If using USB)**
'''bash
sudo nano /etc/sudoers.d/udevadm-nopasswd
'''ini
# Allow user to run udevadm trigger without password
<your_username> ALL=(ALL) NOPASSWD: /usr/bin/udevadm trigger --subsystem-match=sound --action=add
<your_username> ALL=(ALL) NOPASSWD: /usr/bin/udevadm settle
'''

2.6 **Enable permissions (If using USB)**

'''bash
sudo chmod 0440 /etc/sudoers.d/udevadm-nopasswd
'''


3. **Enable and load the service:**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable <service-name>.service
   ```

4. **Useful commands:**
   - Check status: `sudo systemctl status <service-name>.service`
   - Stop service: `sudo systemctl stop <service-name>.service`
   - Start service: `sudo systemctl start <service-name>.service`
