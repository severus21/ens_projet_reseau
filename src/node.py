import logging 

from time import time
from heapq import *

from .misc import *

def get_deadline(_type):
    return {#bootsrap en O(Msg.Hello+Msg.IHU+Msg.NR)
        Msg.Hello:3,
        Msg.IHU:3,
        Msg.NR:3,
        Msg.N:1.5,#pas besoin de beaucoup le retarder(en fait tlv plus t)
        Msg.Data:1.5,
        Msg.IHave:1.5
        }[_type]

class Node:
    def __init__(self, _id, addr, last_paquet=-1, last_ihu=-1, data={}):
        """
        @param data{id_data:seqno max possédé par le noeud}
        """
        self._id = _id
        self.addr = addr
        self.last_paquet = last_paquet
        self.last_ihu = last_ihu
        self.data = data

        #(deadlinei,tlv) priority queue
        self.msgs = []
        self.msgs_size = 0
        self.RTT = 0.3
    
    def __repr__(self):
        return "(%s,%s,%d)" % (hex(self._id), self.addr[0], self.addr[1])

    def _add_tlv(self, tlv, deadline):
        heappush(self.msgs, (deadline, tlv))
        self.msgs_size += len(tlv)

    def add_tlv(self, _type, tlv):
        deadline = time() + get_deadline(_type) 
        self._add_tlv(tlv, deadline)

    def pop_tlv(self):
        deadline, tlv = heappop(self.msgs)
        self.msgs_size -= len(tlv)
        return (deadline, tlv)

    def next_tlvs(self): 
        if not self.msgs:
            return []

        deadline, tlv = self.pop_tlv()
        self._add_tlv(tlv, deadline)
        #2RTT car il faut aussi atteindre l'envoie des autres messages
        if (deadline - 2*self.RTT)>time() and self.msgs_size<BODY_MAX_LEN:#no need to hurry
            return []
        
        tlvs, size = [], 0
        while size < BODY_MAX_LEN and self.msgs:
            deadline,tlv = self.pop_tlv()
            if time()>=deadline:#doit on le droper
                logging.warning("Tlv is outdated before sending it'is bad")
            tlvs.append(tlv)
            size += len(tlv)

        return tlvs    

