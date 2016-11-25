import logging

from math import ceil

from .misc import Msg
from .utility import *

def check_tlv(fct):
    def tlv(*args, **kwargs):
        buff = fct(*args, **kwargs)
        assert(len(buff) < 258)
        return buff
    return tlv

def check_paquet(fct):
    def tlv(*args, **kwargs):
        buff = fct(*args, **kwargs)
        assert(len(buff) < 4096)
        return buff
    return tlv

@check_tlv    
def Hello():
    return b''

@check_tlv
def Pad1():
    return to_bytes(0, 1) 

@check_tlv
def PadN(n):
    return to_bytes(1,1)+ to_bytes(n, 1) + to_bytes(0,n)
        
@check_tlv
def IHU (_id):
    return to_bytes(2,1) + to_bytes(8,1) + to_bytes(_id, 8)  
     
@check_tlv
def NeighbourgRequest ():
    return to_bytes(3,1) + to_bytes(0,1) 
     
@check_tlv
def Neighbourg (l):
    body = b''
    n = len(l)
    m = (8-(n*26)%8 if (n*26)%8!=0 else 0)

    tlv = to_bytes(4,1) + to_bytes(n*26+m,1)
    for (_id, (ip, port)) in l :
        tlv += to_bytes(_id, 8) + ip_string_to_byte(ip) + to_bytes(port, 2)

    return tlv + to_bytes(0,m)
     
@check_tlv
def Data (_id, seqno, data):
    n = len(data)+12
    return to_bytes(5,1)+to_bytes(n,1)+to_bytes(seqno,4)+to_bytes(_id,8)+data 

@check_tlv
def Data_str(_str):    
    buff = _str.encode()
    return to_bytes(32,1)+to_bytes(len(buff),1) + buff

def extract_data(data):
    _len = len(data)
    if _len == 0:
        return ""
    
    #on extrait que le 1er tlv, la sémantique n'est pas définie 
    t0, len0 = data[0], data[1]
    if t0 == 32:
        return data[2:2+2+len0].decode('utf-8')
    else:
        return "Not supported %d" % t0
    
@check_tlv
def IHave(_id,seqno):
    return to_bytes(6,1) + to_bytes(12,1) + to_bytes(seqno,4) + to_bytes(_id,8)   

@check_paquet
def make_paquet (_id, tlvs):
    buff = to_bytes(57,1)+to_bytes(0,1)+to_bytes(sum(map(len,tlvs)),2)
    return buff + to_bytes(_id,8) + b''.join(tlvs)
 
def to_one_tlv (paquet, i):
    _type = paquet[i]
    if (_type == 0):  
        return (Msg.Pad1, None), i+1
    if (_type == 1) or (_type == 3): 
        length = paquet[i+1]
        return (Msg.PadN, None), i + 2 + length
    elif _type == 2:
        length = paquet[i+1]
        _id = int.from_bytes(paquet[i+2:i+10], byteorder='big') 
        return (Msg.IHU, _id),i+2+length
    elif _type == 3:
        length = paquet[i+1]
        return (Msg.NR, None), i+2+length
    elif _type == 4:
        length = paquet[i+1]
        j = i+2
        l = []
        logging.info("Paquet N : %s"% repr(paquet))
        while (j < i+2+length-7):
            _id = int.from_bytes(paquet[j:j+8], byteorder='big')
            ip = ip_byte_to_string(paquet[j+8:j+24])
            port = int.from_bytes(paquet[j+24:j+26], byteorder='big')
            j = j+26
            l.append((_id,(ip,port)))
        return (Msg.N, l), i+2+length 
        
    elif _type == 5:
        length = paquet[i+1]-12
        seqno = int.from_bytes(paquet[i+2:i+6], byteorder='big')
        _id = int.from_bytes(paquet[i+6:i+14], byteorder='big')
        data = paquet[i+14:i+14+length]
        return (Msg.Data, (_id, seqno, data)), i+14+length
    elif _type == 6:
        length = paquet[i+1]
        seqno = int.from_bytes(paquet[i+2:i+6], byteorder='big')
        _id = int.from_bytes(paquet[i+6:i+14], byteorder='big')
        return (Msg.IHave, (_id, seqno)), i+2+length
    else :
        length = paquet[i+1]
        return (None, i+2 +length)
    


def to_tlvs (paquet):
    n = int.from_bytes(paquet[2:4], byteorder = 'big')
    _id = int.from_bytes(paquet[4:12], byteorder = 'big')
    l = []
    i = 12
    while i < 12 + n:
        tlv,i = to_one_tlv(paquet, i)
        if tlv:
            l.append(tlv)
    return (_id, l)

