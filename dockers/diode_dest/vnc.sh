
#!/bin/sh

export  DISPLAY=":1"
Xvfb :1 -screen 0 1280x1024x16 & 
sleep 0.5; 
fluxbox & 
x11vnc -forever -viewonly  -safer & 
terminator -g /home/diode/terminator.cfg; 