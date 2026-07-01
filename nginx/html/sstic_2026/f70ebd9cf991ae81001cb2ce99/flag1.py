import hashlib
from Crypto.Cipher import AES 


########################################################################
#
#   flag_1.tar contains an intermediary flag for step3.
#       This flag will not be taken into account in final ranking
#       it will be used by the team for progress monitoring :)
# 
#   This archive format will also be used for communication
#   by ñ cryptanalyst if needed. 
#
#   Cryptography scheme for this archive HAS NOT BEEN FOOLPROOFED
#
########################################################################

in_file = 'flag_1.tar'

#lobster128 parameters
a_small = ???
b_small = ???

hash_check_small = "d03db0d3bf2498f2d62eb8daf861f293"

def CHALL_SHA256_CHECK(a, b, h):
    hash=hashlib.sha256()
    hash.update(hex(a).encode())
    hash.update(hex(b).encode())

    if (hash.hexdigest()[0:32] != h):
        print("mismatch ??? %s"%hash.hexdigest())
        return False

    return True

def CHALL_PART1_GENKEY(a, b):
    hash=hashlib.sha1()
    hash.update(hex(a).encode())
    hash.update(hex(b).encode())
    key = hash.hexdigest()[:0x20].encode('utf-8')

    return key

def CHALL_PART1_DECRYPT(a, b, in_file, out_file):
    key = CHALL_PART1_GENKEY(a, b)
    
    with open(in_file, 'rb') as f:
        data = f.read()
       
        iv = data[:0x10]
        in_data = data[0x10:]

        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        out_data = cipher.decrypt(in_data)

    with open(out_file, 'wb') as f:
        f.write(out_data)

if not CHALL_SHA256_CHECK(a_small, b_small, hash_check_small):
    print("a and b mismatch ? check parameters with small curve challenge")
    exit()

CHALL_PART1_DECRYPT(a_small, b_small, in_file+'.enc', in_file)