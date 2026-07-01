#!/bin/bash

# openssl passwd -1 '{Thisp@ssw0rdShouldN0tB3GUESSED}'
# $1$dcDPNHKk$sY99GoAbTr33K.ZGrKdq81

useradd  -m  -p '$1$dcDPNHKk$sY99GoAbTr33K.ZGrKdq81' diode_client
useradd  -m  diode

usermod -G diode diode_client

# all data parent directory must be root owned and not writeable by other users
mkdir -p  /sftp/data/in/ /sftp/data/log/ /sftp/data/archive/

# Core cannot be created in current dir (/sftp/data) because not writeable for diode
# the following command must be used on host (readonly in docker)
# echo "/tmp/core.%t" > /proc/sys/kernel/core_pattern

chmod 755 /sftp

chmod g+w /sftp/data/in/
chown -R diode:diode /sftp/data
chown root:root /sftp/data

#fix permission for sftp 
chmod 600 /root/sftp/host

apt update
apt -y install openssh-sftp-server netcat-traditional iproute2 supervisor liblzo2-2
