# sberphoto365
365 challenge bot

manual to install:

# start service
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable sberphoto365.service
sudo systemctl start sberphoto365.service

# check service status
sudo systemctl status sberphoto365.service

# show log
journalctl -u sberphoto365.service -n 50 --no-pager

