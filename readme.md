# SSTIC 2026 : infrastructure

Partial backup from SSTIC 2026 [challenge server](./infra.md). Should contains all players visible data.

## Repository content:

### nginx

Nginx config and data, including: 
* [static challenge inputs](./nginx/html/sstic_2026/f70ebd9cf991ae81001cb2ce99/)
* [Sivi's exfiltration folder](./nginx//html/aoxgulmpgdvaagnd/)
* [an hint for step1](./nginx/html/rdglvlniebdgjmdd/)
* [Sivi's fake startup frontpage](./nginx/html/index.html)

### player_ui

Parts of main player ui, rendered in flask. Steps descriptions can be found in [templates folder](./player_ui/src/templates/).

### dockers

diode_dest & diode_src docker build folders, as used in production environment.
From Step3, a [test package](./nginx/html/sstic_2026/f70ebd9cf991ae81001cb2ce99/step3_test.zip) was supplied to players. 

For each folder, flags (real and test versions) and challenge related data can be found in:
* data/challenger for player supplied version
* data/prod for real environment
Switching from one or the other was done by modifying docker build script (*dockerfile*)

For diode_dst, the monitoring stream (VNC in production) was supposed to be an HLS stream, with ffmpeg adding webcam like artifacts.
Sadly, it was deemed too CPU intensive. HLS can be reactivated by modfifying [diode_dest dockerfile](./dockers/diode_dest/dockerfile) and [diode_dest services](./dockers/diode_dest/services.conf).

uncomment/comment

```
# [program:hls_monitor]
# command=/bin/bash /home/diode/hls.sh
# directory=/home/diode
# autostart=true
# autorestart=true
# user=diode
# stdout_logfile=/home/diode/log/hls.log
# stderr_logfile=/home/diode/log/hls.err

[program:vnc_monitor]
command=/bin/bash /home/diode/vnc.sh
directory=/home/diode
autostart=true
autorestart=true
user=diode
stdout_logfile=/home/diode/log/vnc.log
stderr_logfile=/home/diode/log/vnc.err
```

and
```
COPY --chown=diode --chmod=755 vnc.sh /home/diode/vnc.sh
# COPY --chown=diode --chmod=755 hls.sh /home/diode/hls.sh
```




