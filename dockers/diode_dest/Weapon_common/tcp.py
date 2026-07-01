
import socket
import struct

host = "127.0.0.1"
port = 1515

def tcp_connect():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((host,port))
    return client_socket

def tcp_send_receive(authent_socket,serialized_request):
    #print("tcp_send_receive\n")
    serialized_request_len = len(serialized_request)
    packed_serialized_request_len = struct.pack('>i',serialized_request_len)

    authent_socket.send(packed_serialized_request_len)

    authent_socket.send(serialized_request)

    
    serialized_response_len = authent_socket.recv(4)


    if len(serialized_response_len) == 0:
        print("Disconnected by peer")
        return None

    response_len = struct.unpack('>i',serialized_response_len )[0]
    serialized_response =  authent_socket.recv(response_len)

    return serialized_response

