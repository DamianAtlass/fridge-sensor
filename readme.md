# Fridge-Door-Sensor

## Instructions

### General
All of this is expected to run on a Raspberry Pi Zero 2 w with Raspberry Pi OS installed. 
Follow _mostly_ this [guide](https://tutorials-raspberrypi.de/infrarot-abstandsmessung-mit-dem-raspberry-pi-sharp-gp2y0a02yk0f/) for general instructions.
A description of the GIOP can be found in this [thread](https://forums.raspberrypi.com/viewtopic.php?t=378242).

### Enable SPI devices
```bash
raspi-config
```
Then select _3 Interface Options_ and enable _I4 SPI_. Leave the menu afterward.

### Needed Software packages
 Create a virtual environment and activate it:
```bash
python -m venv .venv
. .venv\bin\activate
```
Clone and install spidev and remaining needed packages:
```bash
git clone https://github.com/doceme/py-spidev.git
pip install -e ./py-spidev
pip install -r requirements.txt
```

## ssh into raspbery py:
on remote machine:
```bash
sudo apt install ssh
sudo apt install sshpass
```
on Raspberry Pi:
```bash
sudo apt install ssh
```
On remote machine:
```bash
shpass -p Pi_user_pw ssh Pi_user@Pi_ip
```

