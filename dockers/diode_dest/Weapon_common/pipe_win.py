import win32pipe,win32file
import struct

PIPE_AUTHENT_TO_WEAPON =r'\\.\pipe\authent_to_weapon'
PIPE_WEAPON_TO_AUTHENT =r'\\.\pipe\weapon_to_authent'


def create_and_connect():
    read_pipe = win32pipe.CreateNamedPipe(
        PIPE_AUTHENT_TO_WEAPON,
        win32pipe.PIPE_ACCESS_INBOUND,
        win32pipe.PIPE_TYPE_BYTE|win32pipe.PIPE_READMODE_BYTE,
        1,0x1000,0x1000,
        0,
        None)
    write_pipe = win32pipe.CreateNamedPipe(
        PIPE_WEAPON_TO_AUTHENT,
        win32pipe.PIPE_ACCESS_OUTBOUND,
        win32pipe.PIPE_TYPE_BYTE|win32pipe.PIPE_READMODE_BYTE,
        1,0x1000,0x1000,
        0,
        None)

    print("Waiting for authent server")
    win32pipe.ConnectNamedPipe(read_pipe,None)
    win32pipe.ConnectNamedPipe(write_pipe,None)

    print("Authent server connected")

    return(read_pipe,write_pipe)


def pipe_read(read_pipe):

    result,data = win32file.ReadFile(read_pipe,4)
    print("Pipe read 4");
    data_len = struct.unpack('>i',data)[0]
    result,serialized_data = win32file.ReadFile(read_pipe,data_len)
    print("Pipe read %d" % data_len);

    return serialized_data


def pipe_send(write_pipe,serialized_message):
    data_len = len(serialized_message)
    win32file.WriteFile(write_pipe,struct.pack('>i',data_len))
    print("Pipe write 4");
    win32file.WriteFile(write_pipe,serialized_message)
    print("Pipe write %d" % data_len);


