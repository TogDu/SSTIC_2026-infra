import struct
import os
from pathlib import Path



PIPE_AUTHENT_TO_WEAPON = "/home/weapon_server/authent_to_weapon"
PIPE_WEAPON_TO_AUTHENT = "/home/weapon_server/weapon_to_authent"


def create_and_connect():

  read_pipe_path = Path(PIPE_AUTHENT_TO_WEAPON)
  write_pipe_path = Path(PIPE_WEAPON_TO_AUTHENT)

  if not read_pipe_path.exists():
    os.mkfifo(PIPE_AUTHENT_TO_WEAPON,0o660);
    os.system("chgrp weapon_trusted %s" % PIPE_AUTHENT_TO_WEAPON)
  if not write_pipe_path.exists():
    os.mkfifo(PIPE_WEAPON_TO_AUTHENT,0o660)
    os.system("chgrp weapon_trusted %s" % PIPE_WEAPON_TO_AUTHENT)

  read_pipe = os.open(PIPE_AUTHENT_TO_WEAPON, os.O_CREAT|os.O_RDONLY)
  write_pipe = os.open(PIPE_WEAPON_TO_AUTHENT, os.O_CREAT|os.O_WRONLY)

  print("Waiting for authent server")

  return(read_pipe,write_pipe)


def pipe_read(read_pipe):

    data = os.read(read_pipe,4)

    print("Pipe read 4")

    if len(data) == 0 :
      print("Pipe disconnected")
      return None


    data_len = struct.unpack('>i',data)[0]
    serialized_data = os.read(read_pipe,data_len)

    print("Pipe read %d" % data_len)

    return serialized_data


def pipe_send(write_pipe,serialized_message):

    data_len = len(serialized_message)
    os.write(write_pipe,struct.pack('>i',data_len))
    print("Pipe write 4")

    os.write(write_pipe,serialized_message)
    print("Pipe write %d" % data_len)


