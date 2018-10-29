import time
import random
from multiprocessing import TimeoutError
import signal

ACK_TYPE = 0
DATA_TYPE = 1


def checksum(*args):
    return sum([sum(list(v)) for v in args]) % 65536


# type_number: 0: ack 1: data
def make_pkt(type_number, seq, data_b=b''):
    # print(seq)
    seq_b = seq.to_bytes(2, byteorder='big')
    type_number_b = type_number.to_bytes(2, byteorder='big')
    checksum_b = checksum(type_number_b, seq_b, data_b).to_bytes(2, byteorder='big')
    return type_number_b + seq_b + checksum_b + data_b


def unpacket(pkt):
    type_number = int.from_bytes(pkt[: 2], 'big')
    seq = int.from_bytes(pkt[2: 4], 'big')
    checksum_v = int.from_bytes(pkt[4: 6], 'big')
    data = pkt[6:]
    return (type_number, seq, data) if checksum_v == checksum(type_number.to_bytes(2, byteorder='big'),
                                                              seq.to_bytes(2, byteorder='big'),
                                                              data) else None
