# Growlab watering
This project allows you to control the watering of your mini-garden using small pumps.

# Enable watering service 

Install Python modules with `pip3`:

```bash
sudo pip3 install -r requirements.txt
```


Install the python script as a service
```shell
sudo cp ~/growlab-watering/watering.service /etc/systemd/system/watering.service
sudo systemctl enable watering.service
sudo systemctl start watering.service
```