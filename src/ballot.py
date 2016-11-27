import logging

from math import ceil

from .misc import Trame 
from .utility import *
from .paquet import Data, to_one_tlv

def ballot_insert(data_id, data):
    tlv = Data(data_id, 0, data)
    return to_bytes(58,1)+to_bytes(0,1)+tlv
    
def ballot_delete(data_id):
    return  to_bytes(58,1)+to_bytes(1,1)+to_bytes(data_id,8)

def parse_ballot(ballot):
    assert(ballot[0] == 58)
    
    if ballot[1] == 0:
        (_, (data_id,_,data)),_ = to_one_tlv(ballot,2) 
        return Trame.Insert, (data_id, data)
    elif ballot[1] == 1:
        return Trame.Delete, from_bytes(ballot[2:])
    
