import socket
import logging
import tempfile
import os
import sys
import lzo

import subprocess
import binascii

import time

from serialize import *

MAX_FILE_SZ = (1* 1024 *1024)

# # Block all incoming traffic
# iptables -A INPUT -j DROP
# # Allow incoming UDP packets on port 1789
# iptables -A INPUT -p udp --dport 1789 -j ACCEPT
# # Allow all outgoing traffic
# iptables -A OUTPUT -j ACCEPT

def print_to_vnc(s, end="\n"):
    print('  '+s, file=sys.stderr, end=end)

def receive_file(sock):
        client = None
        remaining_bytes = MAX_FILE_SZ
        filedata= bytearray()

        # Infinite timeout
        sock.settimeout(None) 

        while remaining_bytes > 0:
            data, address = sock.recvfrom(4096)

            # first datagram must be file size
            if client == None:
                client = address
                if len(data) != 4:
                    logging.error("First datagram must have the file size on 4 bytes, got %d", len(data))
                    return None
                remaining_bytes = int.from_bytes(data, "big", signed=False)
                # do not wait more than 1 sec after file transfert has begun
                sock.settimeout(1) 

            elif client != address:
                logging.error("Client mixing")
                return None
            # receive file
            else:
                if remaining_bytes < len(data):
                    logging.error("Received more data than expected")
                    return None
                filedata += data
                remaining_bytes -= len(data)

        fd, path = tempfile.mkstemp()

        with os.fdopen(fd, "wb") as f:
            f.write(filedata)

        return path

def check_signature(file, sig):
    args = ["crypto/lobster256", "verify", file ,"crypto/lobster_ignition.bin", "crypto/public_key.bin", sig ]
    output = subprocess.run(args, timeout=5)

    # Check the return value
    return output.returncode == 0
    # return True


def get_verified_pkg(file):
    try:
        arch = sstic_arch_t.parse_file(file)
    except BaseException as e:
        logging.error(f"Invalid archive format - {e}")
        return None

    with tempfile.NamedTemporaryFile("w+b", delete_on_close=False) as pkg_file:
        with tempfile.NamedTemporaryFile("w+b", delete_on_close=False) as sig_file:
            pkg_file.write(arch.pkg)
            sig_file.write(arch.sig)
            pkg_file.close()
            sig_file.close()
            if not check_signature(pkg_file.name, sig_file.name):
                return None
    # both files are now deleted

    try:
        pkg =  lzo.decompress(arch.pkg, False, arch.pkg_decompressed_size, algorithm="LZO1X")
    except BaseException as e:
        logging.error(f"Invalid compressed data: {e}")
        return None

    return pkg

def hexdump(data):
    length = len(data)
    sep = '-'
    for i in range(0, length, 16):
        chunk = data[i:i+16]
        offset = i
        part1 = chunk[:8]
        part2 = chunk[8:]
        hex_part1 = sep.join(f"{b:02X}" for b in part1)
        hex_part2 = sep.join(f"{b:02X}" for b in part2)
        hex_part = f"{hex_part1}{sep}{hex_part2}".rstrip()

        hex_crc = binascii.crc32(chunk[:16])
        #pad 
        hex_part += ' '*(48-len(hex_part))

        ascii_str = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in chunk])
        print_to_vnc(f"{offset:04x} {hex_crc:08x} {hex_part} {ascii_str}")

def tcp_connect(h, p):
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect((h,p))
    return client_socket

def tcp_send_receive(sock, req):

    send_len_bytes = len(req).to_bytes(4, "big")
    # print_to_vnc("\n=================================================")
    # print_to_vnc("QUERY sz:%04X"%len(req))
    # hexdump(req)
    # print_to_vnc("=================================================\n")
    sock.send(send_len_bytes + req)
 
    resp_len_bytes = sock.recv(4)

    if not resp_len_bytes:
        logging.warning("Session closed by remote")
        return None
    
    resp_len = int.from_bytes(resp_len_bytes, "big")
    resp =  sock.recv(resp_len)

    print_to_vnc("\n")
    print_to_vnc("=================================================")
    print_to_vnc("resp:%04X"%resp_len)
    hexdump(resp)
    print_to_vnc("end:%08X"%binascii.crc32(resp))
    print_to_vnc("=================================================\n")

    return resp

SESSIONS_LIFO = []

def process_open_session(data):

    sock = tcp_connect("127.0.0.1", 1515)
    if not sock:
        logging.warning("tcp_connect() failed" )
    SESSIONS_LIFO.insert(0, sock)


def process_close_session(data):
    if len(SESSIONS_LIFO) == 0:
        return
    sock = SESSIONS_LIFO.pop(0)
    sock.close()

def process_weapon_msg(data):
    if len(SESSIONS_LIFO) == 0:
        logging.warning("Open a session first")
        return
    sock = SESSIONS_LIFO[0]

    res = tcp_send_receive(sock, data)
    if not res:
        print("no response ?")
        sock = SESSIONS_LIFO.pop(0)
        sock.close()


def process_update_key(data):
    with open('/home/diode/crypto/public_key.bin', 'rb') as f:
        print_to_vnc("old key : ")
        hexdump(f.read())
        print_to_vnc("\n")
        print_to_vnc("new key : ")
        hexdump(data)
    with open('/home/diode/crypto/public_key.bin', 'wb') as f:    
        f.write(data)

def process_not_implemented(data):
    logging.warning("Not implemented")


def process_utils_clear_screan(data):
    print_to_vnc("\033[H\033[2J", end='')

def process_utils_sleep(data):
    sleep_time = 1
    if len(data) > 0:
        sleep_time = data[0]

    print_to_vnc("sleeping %ds"%sleep_time)
    time.sleep(sleep_time)

def process_utils_get_flag_3(data):
    with open('/home/diode/crypto/flag.txt', 'r') as f:
        print_to_vnc(f.read())


BlobType_Hdl =  {
    BlobType.WEAPON_OPEN_SESSION.value : process_open_session,
    BlobType.WEAPON_CLOSE_SESSION.value : process_close_session,
    BlobType.WEAPONS_MSG.value : process_weapon_msg,
    BlobType.UPDATE_SIG_KEY.value : process_update_key,
    BlobType.UPDATE_SIG_EXE.value : process_not_implemented,
    BlobType.UTILS_SLEEP.value : process_utils_sleep,
    BlobType.UTILS_CLEAR_SCREEN.value : process_utils_clear_screan,
    BlobType.UTILS_GET_FLAG_STEP3.value : process_utils_get_flag_3,
}

def process_pkg(data):

    try:
        pkg = pkg_t.parse(data)
        for blob in pkg.body.blobs:
            logging.info(f"processing message {blob.type}")
            BlobType_Hdl[blob.type.intvalue](bytes(blob.data))
    except BaseException as e:
        logging.error(f"Invalid package format - {e}")
        return False
    return True

def run():
    # Create a UDP socket on 1789
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("0.0.0.0", 1789)
    sock.bind(server_address)
    logging.info(f"Listening on {server_address[0]}:{server_address[1]}")

    # Receive data from diode_src
    while True:
        file = None
        pkg = None
        try:
            file = receive_file(sock)
        except socket.timeout:
            logging.error('UDP timeout expired')

        if not file:
            logging.error("receive_file() failed")
            continue
        
        #clear screen
        process_utils_clear_screan(None)

        logging.info("recieved new file")
        pkg = get_verified_pkg(file)
        os.unlink(file)
        if not pkg:
            logging.error("get_verified_pkg() failed")
            continue

        result = process_pkg(pkg)

        if not result:
            logging.error("process_pkg() failed")
            continue
        
        logging.info("File received and processed successfuly")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%m-%d %H:%M:%S')
    run()