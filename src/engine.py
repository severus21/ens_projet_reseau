import logging
import socket
import pickle
import random
import sys, os

from threading import Thread, Event

from itertools import chain
from collections import deque
from random import getrandbits
from os.path import isdir
from time import time
from copy import deepcopy

from .utility import *
from .misc import *
from .scheduler import Scheduler
from .paquet import *

class Engine(Thread):
    def __init__(self, path=None, ip='::', port=None, bootstrap=[]):
        """
        @param path - path to store program data for recovery
        """
        Thread.__init__(self)

        self.starttime = 0

        self.path = path
        self.ip = ip
        self.port = port
        self.bootstrap = bootstrap 


        self.id = random.randint(0, 2**64) 
        self.seqno = 0

        #{"id": (seqno, donnée, date last update)} 
        self.data = {}
        self.owned_data = {}

        #potential_neighbors, {'id': (date dernier paquet, date dernier IHU, (ip, port))}
        self.p_n = {} 
        #unidirectional_neighbors, same
        self.u_n = {}
        #symmetrical_neighbors, set of id of data
        self.s_n = {}
        #{("ip",port:_id}
        self.addrs = {}

        for _id, _addr in self.bootstrap:
            print("bootstrap ", hex(_id))
            self.p_n[_id] = (-1, -1, _addr)
            self.addrs[_addr] = _id

        #list of pending tasks
        self.tasks = deque(maxlen=10**4)
        #message to be send not used
        self.msgs = deque(maxlen=10**4)
        #all launched floods : {"id_data":("seqno_data", data, setofid_neighbourgs, deadline,last_send)}} ie only one flood per id_data
        self.floods = {}
       
        self.scheduler = Scheduler(self.tasks)
        self.tasks.appendleft( (Task.contact_u_n, None) )

        if path and isdir(path):
            self.load()
        
        logging.info("i am %s : %s %d"% (hex(self.id), self.ip, self.port))
    def sendto(self, tlv, addr):
        logging.debug("sending to %s - %s" % (addr[0], str(addr[1])))
        try:
            saddr = ( ipv_2_ipv6(addr[0]), addr[1], 0, 0)
            #saddr = socket.getaddrinfo(addr[0], addr[1], 
            #        proto=socket.IPPROTO_UDP)[0][-1]
            paquet = make_paquet(self.id, [tlv])
            print( saddr, paquet)
            _len = self.sock.sendto( paquet, saddr)
            if len(paquet) != _len:
                logging.warning("sendto incomplete, bytes send %d/%d" % (
                    len(paquet), _len))
        except Exception as e:
            logging.warning("sendto failed : %s" % str(e))

    def load(self):
        pass

    def store(self):    
        pass

    def process_task(self):
        if not self.tasks:
            return

        print("nombre de voisins ", len(self.p_n), len(self.u_n), len(self.s_n))
        _type, args = self.tasks.pop()
        logging.debug("begin process_task %s " % str(_type))
        
        if _type == Task.contact_u_n:
            logging.info("begin sending hello to %d neighbourgs" % 
                (len(self.u_n)+len(self.s_n)))

            for (_,_,_addr) in chain(self.u_n.values(), self.s_n.values()):
                print("hellot to ",_addr)
                print()
                self.sendto( Pad1(), _addr)

            if len(self.s_n) < 5 and self.p_n:
                (_,_,_addr) = random.choice( list(self.p_n.values()))
                self.sendto( Pad1(), _addr)
        elif _type == Task.ihu_s_n:
            logging.info("begin sending IHU to %d neighbourgs" % len(self.s_n)) 

            for _id, (_,_,_addr) in chain(self.u_n.items(), self.s_n.items()):
                self.sendto( IHU(_id), _addr)
        elif _type == Task.check_neighborgs:
            logging.info("checking if there is enought neighbours")

            if len(self.p_n) < 5 and self.s_n:
                logging.info("not enought neighbours, requesting others")
                (_,_,_addr) = random.choice( list(self.s_n.values()))
                self.sendto( NeighbourgRequest(), _addr)
        elif _type == Task.update_data:
            logging.info("updating data")

            for id_data  in self.owned_data:
                seqno, data, last_update = self.data[id_data]

                self.data[id_data] = (seqno+1, data, time())
                self.tasks.appendleft( (task.flood, (id_data, seqno+1, data)) )  
        elif _type == Task.prune_data:
            del_keys = []
            for id_data, (seqno, data, last_update) in self.data:
                if last_update + 35*60 < time() and (key not in self.owned_data):
                    del_keys.append(id_data)

            logging.info("pruning %d outdated data" % len(del_keys))

            for key in del_keys:
                del self.data[key]
        elif _type == Task.flood:
            id_data, seqno_data, data = args
            if id_data in self.floods:
                logging.debug("id data already in floods, this flood will be postpone")
                (seqno_flood, _,_,_) = self.floods[id_data]
                if seqno_flood < seqno_data:
                    #interruption du flood pour la notre??
                    self.tasks.appendleft( (Task.flood, args) )
                else:
                    logging.debug("already flooding more recent content")
            else:
                logging.info("begin flooding (%s, %d)" % (hex(id_data), seqno_data))
                self.floods[id_data]=(seqno_data, data, set(self.s_n.keys()), None, 0)
        elif _type == Task.prune_neighborgs:
            logging.info("pruning neighbourgs")

            for _id, (last_p, last_ihu, addr) in list(self.u_n.items()):
                if last_p + 100 < time():
                    print(self.u_n)
                    del self.addrs[ self.u_n[_id][-1] ]
                    del self.u_n[_id]
            for _id, (last_p, last_ihu, addr) in list(self.s_n.items()):
                print(_id, last_p, last_ihu, addr)
                if last_p + 150 < time() or last_ihu + 300 < time():
                    del self.addrs[ self.s_n[_id][-1] ]
                    del self.s_n[_id]
        elif _type == Task.refresh_ihm:
           os.system('clear')
           title = "Node id: %s, Uptime: %ds" % (hex(self.id), int(time()-self.starttime))
           print( center(title) )
           print( center(underline(title)) )
           print( "\n\n")
          
           for name, htbl in [("Symetrical", self.s_n), 
                   ("Unidirectionnal",self.u_n), ("Potential", self.p_n)]:
                title = "%s neighbourgs:" % name

                print( title )
                print( underline(title) )

                n_data = ""
                for _id, (last_paquet, last_ihu, addr) in htbl.items():
                    l_p = int(time()-last_paquet) if last_paquet >= 0 else -1 
                    l_i = int(time()-last_ihu) if last_ihu >= 0 else -1 
                    n_data = "%s\n  %s  %s:%d  %d  %d" % (n_data, hex(_id),
                            addr[0], addr[1], l_p, l_i)
                print(n_data)
                print( "\n")

           title = "Data :"
           print(title)
           print( underline(title))

           b_data = ""
           for _id, (seqno, data, _) in self.data.items():
               b_data = "%s\n  %s  %d  %s" % (b_data, hex(_id), seqno, data)
           print( b_data )
    def process_recv(self, data, addr):
        if not data:
            return 

        _id, tlvs = to_tlvs(data)
        logging.debug("begin process_recv %s" % hex(_id))

        #maintenance de la liste des paquets
        if (_id not in self.u_n) and (_id not in self.s_n):
            if _id in self.p_n:
                del self.addrs[ self.p_n[_id][-1] ]
                del self.p_n[_id]

            logging.info("%s added to unidirectionnal neighbours" % hex(_id))
            self.addrs[addr] = _id
            self.u_n[_id] = (time(), -1, addr)
            print([hex(keys) for keys in self.u_n.keys()])
            print([hex(keys) for keys in self.p_n.keys()])
        elif _id in self.u_n:
            self.u_n[_id] = (time(), self.u_n[_id][1], addr)    
        elif _id in self.s_n:    
            self.s_n[_id] = (time(), self.s_n[_id][1], addr)    

        if not tlvs:
            return None
        
        for (_type, args) in tlvs:
            logging.debug("begin process tlv %s" % str(_type))
            if _type == Msg.Pad1 or _type == Msg.PadN:
                pass
            elif _type == Msg.IHU:
                if args != self.id:
                    continue
                logging.debug("Received IHU from %s and processing" % hex(_id))
                if _id in self.u_n:
                    del self.u_n[_id]
                if _id in self.p_n:
                    del self.p_n[_id]
                
                self.s_n[_id] = (time(), time(), addr)
                print(self.s_n)
                print(self.p_n)
            elif _type == Msg.NR:
                logging.info("Received NeighbourgRequest and processing")
                #filter lui même
                ids = random.sample(list(self.s_n.keys()), min(10, len(self.s_n)))
                self.sendto(Neighbourg([(i,self.s_n[i][-1]) for i in ids]), addr)
            elif _type == Msg.N:
                logging.info("Received Neighbourg and processing")
                for (id0, addr0) in args: 
                    if id0 != self.id:
                        self.p_n[id0] = (time(), -1, addr0)

            elif _type == Msg.Data:
                id_data, seqno_data, data_pub = args
                logging.info("Received Data (%s,%d) and processing" % (hex(id_data), seqno_data))
                print("data", data_pub)
                
                self.sendto(IHave(id_data, seqno_data), addr)
                
                if id_data in self.floods:
                    (tmp_sqno,_,L,_,_) = self.floods[id_data]
                    if seqno_data >= tmp_sqno:
                        L.remove(_id)
                    continue

                if id_data in self.data:
                    if self.data[id_data][0] < seqno_data:
                        self.data[id_data](seqno_data, data_pub, time())
                        self.tasks.appendleft( (Task.flood, (id_data, seqno_data, data_pub)) )  
                else:
                    self.tasks.appendleft( (Task.flood, (id_data, seqno_data, data_pub)) )  

            elif _type == Msg.IHave:
                id_data, seqno_data= args
                logging.info("Received IHave (%s,%d) and processing" % (hex(id_data), seqno_data))
                
                if id_data not in self.floods:
                    continue
                
                (tmp_sqno,_,L,_,_) = self.floods[id_data]
                if seqno_data >= tmp_sqno:
                    L.remove(_id)

    def proccess_floods(self):
        if not self.floods:
            return 

        logging.debug("begin process floods")
        #cleaning floods, ie deleting outdated floods(11s)
        del_keys = []
        print(self.floods)
        for key,(seqno,_,L,deadline,_) in self.floods.items():
            if (deadline and deadline < time()) or not L:
                del_keys.append( key )
                logging.debug("removing outadated flood : %s,%d" % (hex(key), seqno) )

        for key in del_keys:
            del self.floods[key]
        
        #send Data each 3s    
        for id_data, (seqno_data, data, L, deadline, last_send) in self.floods.items():     
            if last_send + 3 < time():
                logging.info("flooding %s,%d to %d nodes" %(hex(id_data), seqno_data, len(L)))
                for _id in L:
                    if _id in self.s_n:
                        self.sendto( Data(id_data, seqno_data, data), self.s_n[_id][-1])       
                    else:
                        L.remove(_id)
                self.floods[id_data] = (seqno_data, data, L, deadline if deadline else time()+11, time())
        
    def run(self):
        """
        main loop
        """
        try:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
            self.sock.bind((self.ip, self.port ))
            self.sock.settimeout(0.001)
        except Exception as e:
            print((self.ip, self.port))
            logging.error( "Socket init failed : %s" % str(e) )
            return False 
        logging.debug("socket init (%s,%d): success!" % (self.ip, self.port))

        self.scheduler.start()

        self.starttime = time()

        while True:
            #logging.debug("begin mainloop")
            try:
                try:
                    data, addr=self.sock.recvfrom(PAQUET_MAX_LEN)
                    self.process_recv( data, addr )
                except socket.timeout:
                    pass
                
                
                self.process_task()
                self.proccess_floods() #probablement trop de priorité donnée au floods
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.warning("error unknow in main loop %s in %s at line %d : %s" % (str(exc_type), str(fname), exc_tb.tb_lineno, str(e)))
