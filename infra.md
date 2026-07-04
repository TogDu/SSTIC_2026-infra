## Challenge server: 

## overview

```
            +-----------+
            |           |  /* ------> filer folder + autoindex
HTTP/80 <-->|  NGINX:   | 
            |           |  /step/* --> 127.0.0.1:8080
            +----- -----+               |
                                        |
                                        |       
                                +---------------+
                                |               |   - player UI (steps descritpion & flag mgt)
                                |   FLASK       |   - handle player's docker creation & lifetime
                                |               |-----+
                                |---------------+     |
                                                      |       
                                             +---------------+
                                             |               |
                                             |   kube&all    |   spawn an isolated S.A.F.E instance 
                                             |               |       - diode_dest + firewall
                                             +---------------+       - diode_src

                        
                        +-----------------------------------------------------------------------+
                        |                           ONE SAFE INSTANCE                           |
                        |                                                                       |
                        |           10.0.55.100                       10.0.55.150               |
                        |       +---------------+               +-------------------+           |   
                        |       |   diode_src   |               |     diode_dst     |           |
                        | :2222 |               |               |udp:1789: server   |           |
rand[30000:32767] <---> | <---> |   SFTP:*:2222 |<------------->|                   |           |
                        |       +---------------+       +------>|vnc:5900           |           |
                        |                               |       |  (or nginx+HLS)   |           |
                        |       +---------------+       |       +-------------------+           |
                        | :5900 |  alpine/socat |       |                                       |
rand[30000:32767] <---> | <---> | proxy for vnc |<------+                                       |
                        |       |               |                                               |
                        |       +---------------+                                               |
                        |                                                                       |
                        |       +---------------+                                               |
                        |       | firewall(FIX) |  (hotfix for not applicated netpol)           |
                        |       |   player ip   |     drop all incoming traffic                 |
                        |       |   filtering   |     except comming from player IP             |
                        |       +---------------+                                               |
                        |                                                                       |
                        +-----------------------------------------------------------------------+
```