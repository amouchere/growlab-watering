# Growlab watering
This project allows you to control the watering of your mini-garden using small pumps.

# Hardware

* A Raspberry Pi
* One or many relay modules (VCC 5V)
* One or many micro submersible mini water pumps
* External battery 5V
# Installation

```bash
git clone git@github.com:amouchere/growlab-watering.git
```

# Enable watering service 

Install Python modules with `apt`:

```bash
sudo apt update -qy && \
  sudo apt install -qy git\
  python3 \
  python3-tz \
  python3-requests
```


Install the python script as a service
```shell
sudo cp ~/growlab-watering/watering.service /etc/systemd/system/watering.service
sudo systemctl enable watering.service
sudo systemctl start watering.service
```