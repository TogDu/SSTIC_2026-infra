import struct
from enum import Enum


class ValueType(Enum):
    STRING = 0
    FLOAT = 1


class OperationCode(Enum):
    AUTHENT = 0
    GET_TARGET = 1
    SET_TARGET = 2
    FIRE = 3
    DISARM = 4
    GET_VERSION = 5
    IMPERSONATE = 6

class Message:
    def __init__(self,operation_code):
        self.operation_code = operation_code
        self.error_code = 0
        self.values = []


    def add_string(self,string_value):
        self.values.append((ValueType.STRING,string_value))

    def add_float(self,float_value):
        self.values.append((ValueType.FLOAT,float_value))

    def check_error_code(self):
        if self.error_code == 0:
            return True
        elif self.error_code == 3:
            print("Privileges not held for user :%s" % self.get_string(0))
            return False
        else:
            return False

    def get_string(self,index):
        return self.values[index][1]

    def get_float(self,index):
        return self.values[index][1]



    def pack(self):
        packed_bytes = bytearray(0)
        packed_bytes +=struct.pack('>bhh',self.operation_code.value,0,len(self.values))

        for v in self.values :
            packed_tlv_bytes = bytearray(0)
            v_type = v[0]
            v_value = v[1]
            if v_type == ValueType.STRING:
                packed_tlv_bytes+= struct.pack('>b',0)
                packed_tlv_bytes+= struct.pack('>h',len(v_value)+1)
                encoded_value = v_value.encode("utf-8") + b'\x00'
                packed_tlv_bytes+= encoded_value
            elif v_type == ValueType.FLOAT:
                packed_tlv_bytes+= struct.pack('>b',1)
                packed_tlv_bytes+= struct.pack('>h',8)
                packed_tlv_bytes+= struct.pack('>d',v_value)
            else:
                print(f"Unknown type: {v_type}")
                throw()
            packed_bytes += packed_tlv_bytes

        return packed_bytes


    def unpack(packed_bytes):
        msg = Message(0)
        msg.values = []

        header = packed_bytes[0:5]
        remaining_data = packed_bytes[5:]

        msg.operation_code,msg.error_code,value_count = struct.unpack('>bhh',header)

        for i in range(0,value_count):
            value_type,value_data_len = struct.unpack('>bh',remaining_data[0:3])
            if 0 == value_type:
                value = remaining_data[3:3+value_data_len].decode('utf8')
            else:
                value = float(struct.unpack('>d',remaining_data[3:3+value_data_len])[0])

            msg.values.append((value_type,value))

            remaining_data = remaining_data[3+value_data_len:]

        return msg

