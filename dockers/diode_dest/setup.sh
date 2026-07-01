#!/bin/sh

# setup step3
useradd -m diode

# setup step4&step5
adduser weapon_authent
adduser weapon_server

groupadd weapon_trusted
usermod -G weapon_trusted weapon_authent
usermod -G weapon_trusted weapon_server

chgrp weapon_trusted  /home/weapon_server
chmod ug+rwx  /home/weapon_server


mkdir -p /home/weapon_authent/chal/

mkdir -p /home/weapon_server/chal/Weapon_server
mkdir -p /home/weapon_server/chal/Weapon_common

# log
mkdir /log
chmod 777 /log
touch /log/weapon_server.log /log/diode_dest.log /log/weapon_supervisor.log
chmod 666 /log/*