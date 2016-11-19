import logging
import socket
import pickle

from collections import deque
from random import getrandbits
from os.path import isdir
from time import time
from copy import deepcopy

from .utility import *
from .misc import *
from .scheduler import scheduler


class Engine:
    def __init__(self, path=None, ip=None, port=None):
        """
        @param path - path to store program data for recovery
        """
        self.path = path
        self.ip = ip
        self.port = port
        if path and isdir(path):
            self.load()

        self.id = (getrandbits(8).to_bytes(8, byteorder='little')
        self.seqno = 0

        #{"id": (seqno, donnée, date last update)} 
        self.data = {}
        
        #potential_neighbors, {'id': (date dernier paquet, date dernier IHU, (ip, port))}
        self.n_p = {} 
        #unidirectional_neighbors, same
        self.u_n = {}
        #symmetrical_neighbors, same
        self.s_n = {}
        
        #list of pending tasks
        self.tasks = deque(maxlen=10**4)
        #message to be send not used
        self.msgs = dequet(maxlen=10**4)
        #all launched floods : {"id_data":{"seqno_data": (data, listofid_neighbourgs, deadline)}}
        self.floods = {}
        
   def load(self):
        pass

    def store(self):    
        pass

    def process_task(self):
    
    def process_recv(self, data, addr):
        _id, tlvs = to_tlvs(data)
       
        #maintenance de la liste des paquets
        if _id not in self.u_n and _id not in self.s_n:
            self.u_n[_id] = (time(), -1, addr)
        elif _id in self.u_n:
            self.u_n[_id] = (time(), self.u_n[_id][2], addr)    
        elif _id in self.s_n:    
            self.s_n[_id] = (time(), self.s_n[_id][2], addr)    

        if not tlvs:
            return None
        
        for (_type, args) in tlvs:
            if _type == Msg.Pad1 or _type == Msg.PadN:
                pass
            elif _type == Msg.IHU:
                if args[0] != self.id:
                    continue

                if _id in self.u_n:
                    del self.u_n[_id]
                elif _id in self.p_n:
                    del self.p_n[_id]
                else:
                    self.s_n[_id] = (time(), time(), addr)
            elif _type == Msg.NR:
                ids = random.sample(list(self.s_n.keys()), min(10, len(self.s_n))
                self.sock.sendto(Neighbours([(i,self.s_n[-1]) for i in ids]), addr)
            elif _type == Msg.N:
                for (id0, addr0) in args:  
                    self.p_n[id0] = (time(), -1, addr0)
            elif _type == Msg.Data:
                id_data, seqno_data, data_pub = args
                
                self.sock.sendto(IHave(id_data, seqno_data))
                
                if id_data in self.floods:
                    for (_,L,_) in self.floods[id_data].values:
                        L.remove(_id)
                    continue

                if id_data in self.data:
                    if self.data[id_data][0] < seqno_data:
                        self.data[id_data](seqno_data, data_pub, time())
                        self.tasks.append_left( (task.flood, id_data, seqno_data, data_pub) )  
                else:
                    self.tasks.append_left( (task.flood, id_data, seqno_data, data_pub) )  

            elif _type == Msg.IHave:


    def run(self):
        """
        main loop
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.bind((UDP_IP, UDP_PORT))
            self.settimeout(1)
        except Exception as e:
            logging.error( "Socket init failed : %s" % str(e) )
            return False 


        while True:
            try:
                data, addr=self.sock.recvfrom(65535)
                self.process_recv( data, addr )
            except timeout:
                pass

            self.process()
