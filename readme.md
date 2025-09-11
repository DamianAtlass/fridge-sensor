# Fridge-Door-Sensor

## Instructions

### General
This is an attempt of developing a sensor for a fridge which detects if the door has been left open for some time using 
standard electronics components and some python programming.  

This is expected to run on a Raspberry Pi Zero 2 w with Raspberry Pi OS installed. 
Follow _mostly_ this [guide](https://tutorials-raspberrypi.de/infrarot-abstandsmessung-mit-dem-raspberry-pi-sharp-gp2y0a02yk0f/) for general instructions. A buzzer and an LED were added as well.
A description of the GIOP can be found in this [thread](https://forums.raspberrypi.com/viewtopic.php?t=378242).

### Enable SPI devices
```bash
raspi-config
```
Then select _3 Interface Options_ and enable _I4 SPI_. Leave the menu afterward.

### Needed Software packages
 
```bash
# Clone the repository:
git clone https://github.com/DamianAtlass/fridge-sensor.git
cd fridge-sensor
# Create a virtual environment and activate it:
python3 -m venv .venv
. .venv/bin/activate

# Install all requirements:
pip install -r requirements.txt
```

**If** spidev doesn't install, try this:
```bash
git clone https://github.com/doceme/py-spidev.git
pip install -e ./py-spidev
```

Add this library, if needed:
```bash
sudo apt update
sudo apt install libopenblas-dev
```
### Setup email notifications
If you do not wish to receive email notifications you can simply set the flag *-nomail* and skip this step. 
Otherwise, fill the *.env_template* and rename it to *.env* . Make sure that you set the appropriate setting in your email client of choice.


### Run the script
```bash
python main.py
```
Options: \
-s : silent, deactivate buzzer \
-o [float] : add (usually positive) offset to distance calculation (default: 0.5) \
-nomail : set if you do not wish to receive email notifications or do not have the .env setup

## Run the script automatically when the device starts

Create a run script and make it executable. Pass any optional parameters listed above if you want.
```bash
echo "python $(pwd)/main.py" > run.sh
chmod +x run.sh
```

Add a cronjob to run it on startup. Enter the cronjob interface with:
```bash
sudo crontab -e
```

Enter `@reboot bash [PATH]/foo.sh &`. Replace [PATH] with the path to run.sh's parent directory. Save and close the 
file.

It should now automatically start on system boot.

### Stop the script when running as cronjob
You might want to stop it whne your about to change something or debug. To do so, find the process by e.i looking for 
the script path and remember the process id (PID):
```bash
ps -ef
```

Kill the process:
```bash
sudo kill PID
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
On remote (linux) machine:
```bash
shpass -p Pi_user_pw ssh Pi_user@Pi_ip
```

On windows use
```bash
 ssh Pi_user@Pi_ip
```
...and enter the password.