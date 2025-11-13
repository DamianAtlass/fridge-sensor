# Fridge-Door-Sensor

## Instructions

### General
This personal project was a successful attempt at developing a device for a fridge which detects meant to detect an 
open door and take countermeasures in the form of noise alerts and email notifications using 
standard electronics components and python programming. There is  also a script that evaluates the logged data. 

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
python src/main.py
```
Options: \
-s : silent, deactivate buzzer \
-o [float] : add (usually positive) offset to distance calculation (default: 0.5) \
-nomail : set if you do not wish to receive email notifications or do not have the .env setup
-j [float] : set threshold for detecting of the door is ajar. Doing so will respond with more 
aggressive beeping very early. Pass a high negative number (like -500) to disable it (it is on by default) 

Alternativly, just run the run.sh script.


## Run the script automatically when the device starts

The file _run.sh_ will be used to run the script properly. Be sure to make it executable and pass any optional 
parameters listed above if you want.
```bash
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
the script path and remember the process id (PID). Look for the main.py process:
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

## Copy logs for plotting using scp
```bash
scp Pi_user@Pi_ip:path_to_repository/logs.csv logs.csv
```
...and enter the password.

## Images

![image of box](/images/image1.png)