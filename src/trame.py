import logging

from math import ceil

from .misc import Trame 
from .utility import *
from .paquet import Data, to_one_tlv

def trame_insert(data_id, data):
    tlv = Data(data_id, 0, data)
    return to_bytes(58,1)+to_bytes(0,1)+tlv
    
def trame_delete(data_id):
    return  to_bytes(58,1)+to_bytes(1,1)+to_bytes(data_id,8)

def parse_trame(trame):
    assert(trame[0] == 58)
    
    if trame[1] == 0:
        (_, (data_id,_,data)),_ = to_one_tlv(trame,2) 
        return Trame.Insert, (data_id, data)
    elif trame[1] == 1:
        return Trame.Delete, from_bytes(trame[2:])
    
