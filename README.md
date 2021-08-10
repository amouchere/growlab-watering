sudo cp ~/growlab-watering/watering.service /etc/systemd/system/watering.service
sudo systemctl enable watering.service
sudo systemctl start watering.service