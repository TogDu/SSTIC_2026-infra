#!/bin/bash

#limit log size with cron
echo "* * * * * /usr/bin/echo '' > /log/weapon_server.log"  | crontab -

source venv/bin/activate
export PYTHONUNBUFFERED=1
python3 Weapon_server/run.py