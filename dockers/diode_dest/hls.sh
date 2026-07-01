#!/bin/sh

export  DISPLAY=":1"
Xvfb :1 -screen 0 1280x1024x16 & 
sleep 0.5; 
fluxbox & 

terminator -g /home/diode/terminator.cfg &

ffmpeg \
 -f x11grab -video_size 1280x1024 \
 -framerate 25 -i :1 \
 -filter_complex "\
   boxblur=1.5:1,\
   noise=alls=12:allf=t+u,\
   eq=brightness='0.01*sin(t*0.5)':contrast=1.05:saturation=1.02,\
   lenscorrection=k1=-0.015:k2=0.005,\
   drawgrid=width=iw:height=4:thickness=1:color=black@0.05,\
   drawtext=text='monitor -- INTERNAL USE ONLY -- %{localtime}':x=10:y=985:fontsize=20:fontcolor=red@0.7\
   " \
 -c:v libx264 \
 -preset veryfast \
 -tune zerolatency \
 -profile:v baseline \
 -level 3.0 \
 -pix_fmt yuv420p \
 -b:v 1200k \
 -maxrate 1500k \
 -bufsize 2000k \
 -g 50 \
 -f hls \
 -hls_time 2 \
 -hls_list_size 5 \
 -hls_flags delete_segments \
 /home/diode/hls/out.m3u8 &

cd /home/diode/hls;
python3 -m http.server 5900;


