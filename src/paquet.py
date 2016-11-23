import logging

from .misc import Msg
from .utility import *



def Pad1 () :
    return (0).to_bytes(1, byteorder = 'big') 
        
        
def PadN (mbz) :
    n = len(mbz)
    _type = (1).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return _type + length+mbz
        
def IHU (_id):
    _id = (_id).to_bytes(8, byteorder='big')
    n = len(_id)
    _type = (2).to_bytes(1, byteorder = 'big')
    length = (8).to_bytes(1, byteorder = 'big')
    return _type + length + _id
     
def NeighbourgRequest ():
    _type = (3).to_bytes(1, byteorder = 'big')
    length = (0).to_bytes(1, byteorder = 'big')
    return _type + length
     
def Neighbourg (l):
    body = b''
    for (_id, (ip, port)) in l :
        body += (_id).to_bytes(8, byteorder='big')+ip_string_to_byte(ip)+port.to_bytes(2, byteorder='big')
    n = len(body)
    if n % 8 !=0:
        body += (0).to_bytes(8-n%8, byteorder = 'big')
        n+= 8-n%8
    _type = (4).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return _type + length + body
     
def Data (_id, seqno, data):
    _id = (_id).to_bytes(8, byteorder='big')
    seqno =(seqno).to_bytes(4, byteorder = 'big')
    n = len(seqno)+len(_id)+len(data)
    _type = (5).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return _type + length + seqno +_id +data
     
def IHave(_id,seqno):
    _id = (_id).to_bytes(8, byteorder='big')
    seqno =(seqno).to_bytes(4, byteorder = 'big')
    n = len(seqno)+len(_id)
    _type = (6).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return _type + length + seqno +_id 


def make_paquet (_id0, l):
    body = b''
    for tlv in l :
        body += tlv

    _id = (_id0).to_bytes(8, byteorder='big')   
    magic = (57).to_bytes(1, byteorder = 'big')
    version = (0).to_bytes(1, byteorder = 'big')
    n = len(body)
    length = n.to_bytes(2, byteorder = 'big')
    return magic + version + length + _id + body
 
   
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

