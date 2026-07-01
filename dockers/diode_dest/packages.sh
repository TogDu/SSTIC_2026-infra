#!/bin/bash

apt update

# packages for diode_dest.py
apt install -y python3-pip python3-construct python3-lzo 

# package for camera
apt install -y xvfb fluxbox terminator supervisor ffmpeg

# package for vnc
apt install -y xvfb fluxbox terminator supervisor x11vnc

# for step5 and others
apt install -y python3-venv iproute2 netcat-traditional cron