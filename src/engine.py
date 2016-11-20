import logging
import socket
import pickle
import itertools

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

        self.id = (getrandbits(8).to_bytes(8, byteorder='big'))
        self.seqno = 0

        #{"id": (seqno, donnée, date last update)} 
        self.data = {}
        self.owned_data = {}

        #potential_neighbors, {'id': (date dernier paquet, date dernier IHU, (ip, port))}
        self.n_p = {} 
        #unidirectional_neighbors, same
        self.u_n = {}
        #symmetrical_neighbors, set of id of data
        self.s_n = {}
        
        #list of pending tasks
        self.tasks = deque(maxlen=10**4)
        #message to be send not used
        self.msgs = dequet(maxlen=10**4)
        #all launched floods : {"id_data":("seqno_data", data, setofid_neighbourgs, deadline,last_send)}} ie only one flood per id_data
        self.floods = {}
        
   def load(self):
        pass

    def store(self):    
        pass

    def process_tasks(self):
        _type, args = self.tasks.pop_right()
        
        if _type == Task.contact_u_n:
            for (_,_,_addr) in itertools.chain(self.u_n.values(), self.s_n.values())
                self.sock.sendto( Pad1(), _addr)

            if len(self.s_n) < 5 ans self.p_n:
                (_,_,_addr) = random.choice( list(self.p_n.values()))
                self.sock.sendto( Pad1(), _addr)
        elif _type == Task.ihu_s_n:    
            for _id, (_,_,_addr) in itertools.chain(self.u_n.items(), self.s_n.items())
                self.sock.sendto( IHU(_id), _addr)
        elif _type == Task.check_neighborgs:
            if len(self.p_n) < 5 and self.s_n:
                (_,_,_addr) = random.choice( list(self.s_n.values()))
                self.sock.sendto( NeighbourRequest(), _addr)
        elif _type == Task.update_data:
            for id_data  in self.owned_data:
                seqno, data, last_update = self.data[id_data]

                self.data[id_data] = (seqno+1, data, time())
                self.tasks.append_left( (task.flood, id_data, seqno+1, data) )  
        elif _type == Task.prune_data:
            del_keys = []
            for id_data, (seqno, data, last_update) in self.data:
                if last_update + 35*60 < time():
                    del_keys.append(id_data)
            for key in del_keys:
                if key not in self.owned_data:
                    del self.data[key]
        elif _type == Task.flood:
            id_data, seqno_data, data = args
            if id_data in self.flood:
                logging.debug("id data already in floods, this flood will be postpone")
                self.tasks.append_left( Task.flood, args)
            else:
                self.floods[id_data]=(seqno_data, data, set(self.s_n.keys()), None, 0)
        elif _type == Task.prune_neighborgs:
            for _id, (last_p, last_ihu, addr) in list(self.u_n.items()):
                if last_p + 100 < time():
                    del self.u_n[_id]
            for _id, (last_p, last_ihu, addr) in list(self.s_n.items()):
                if last_p + 150 < time() or last_ihu + 300 < time():
                    del self.s_n[_id]

            
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
                
                self.sock.sendto(IHave(id_data, seqno_data), addr)
                
                if id_data in self.floods:
                    (tmp_sqno,_,L,_,_) = self.floods[id_data]
                    if seqno_data >= tmp_sqno:
                        L.remove(_id)
                    continue

                if id_data in self.data:
                    if self.data[id_data][0] < seqno_data:
                        self.data[id_data](seqno_data, data_pub, time())
                        self.tasks.append_left( (task.flood, id_data, seqno_data, data_pub) )  
                else:
                    self.tasks.append_left( (task.flood, id_data, seqno_data, data_pub) )  

            elif _type == Msg.IHave:
                id_data, seqno_data= args
                
                if id_data not in self.floods:
                    continue
                
                (tmp_sqno,_,L,_,_) = self.floods[id_data]
                if seqno_data >= tmp_sqno:
                    L.remove(_id)

    def proccess_floods(self):
        #cleaning floods, ie deleting outdated floods(11s)
        del_keys = [] 
        for key,(_,_,L,deadline,_) in self.floods:
            if (deadline and deadline < time()) or not L:
                del_keys.append( key )
        
        for key in del_keys:
            del self.floods[key]
        
        #send Data each 3s    
        for id_data, (seqno_data, data, L, deadline, last_send) in self.floods.items():     
            if last_send + 3 < time():
                for _id in L:
                    if _id in self.s_n:
                        self.sock.sendto( Data(id_data, seqno_data, data), self.s_n[_id][-1])       
                    else:
                        L.remove(_id)
                self.floods[id_data] = (seqno_data, data, L, deadline if deadline else time()+11, time())
        
    def run(self):
        """
        main loop
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
            self.sock.bind((UDP_IP, UDP_PORT))
            self.settimeout(0.001)
        except Exception as e:
            logging.error( "Socket init failed : %s" % str(e) )
            return False 


        while True:
            self.process_neighbours()

            try:
                data, addr=self.sock.recvfrom(PAQUET_MAX_LEN)
                self.process_recv( data, addr )
            except timeout:
                pass
            
            self.process_task()
            self.proccess_floods() #probablement trop de priorité donnée au floods
            
