import logging
import socket
import pickle
import random
import sys, os
import traceback


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
from .ballot import *
from .node import Node
from .flood import Flood

TIMEOUT = 0.005

class Engine(Thread):
    def __init__(self, path=None, ip='::', port=None, bootstrap=[], data=[],
            pub_key=None, private_key=None):
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
        #self.seqno = 0
        self.private_key = private_key
        self.pub_key = pub_key

        #{"id": (seqno, donnée, date last update)} 
        self.data = {}
        self.owned_data = set()#ids 
        for i,d in enumerate(data):
            _id = self.id if i == 0 else  random.randint(0, 2**64)
            self.data[_id] = (0, d, time())
            self.owned_data.add( _id )
        #potential_neighbors, {'id': node obj}
        self.p_n = {} 
        #unidirectional_neighbors, same
        self.u_n = {}
        #symmetrical_neighbors, set of id of data
        self.s_n = {}
        #{("ip",port:_id}

        for _id, _addr in self.bootstrap:
            self.p_n[_id] = Node(_id, _addr)

        #list of pending tasks
        self.tasks = deque(maxlen=10**4)
        #message to be send( type, tlv, deadline)
        self.msgs = deque(maxlen=10**4)
        #all launched floods : {"id_data":Flood}
        self.floods = {}
       
        self.scheduler = Scheduler(self.tasks)
        self.tasks.appendleft( (Task.contact_u_n, None) )

        if path and isdir(path):
            self.load()
        
        logging.info("i am %s : %s %d"% (hex(self.id), self.ip, self.port))

    def send(self, paquet, addr):
        try:
            saddr = ( ipv_2_ipv6(addr[0]), addr[1], 0, 0)
            _len = self.sock.sendto( paquet, saddr)
            if len(paquet) != _len:
                logging.warning("sendto incomplete, bytes send %d/%d" % (
                    len(paquet), _len))
        except Exception as e:
            logging.warning("sendto failed : %s" % str(e))

    def process_send(self):
        for node in chain(self.s_n.values(), self.p_n.values(), self.u_n.values()):
            tlvs = node.next_tlvs()
            if tlvs:
                logging.info("tlvs aggregated and send to %s" % node)
                self.send(make_paquet(self.id, tlvs), node.addr)

    def load(self):
        pass

    def store(self):    
        pass

### Tasks definitions
    def contact_u_n(self):
        logging.info("begin sending hello to %d neighbourgs" % 
            (len(self.u_n)+len(self.s_n)))

        for node in chain(self.u_n.values(), self.s_n.values()):
            node.add_tlv(Msg.Hello, Hello())

        if len(self.s_n) < 5 and self.p_n:
            node = random.choice( list(self.p_n.values()))
            node.add_tlv(Msg.Hello, Hello())
    
    def ihu_s_n(self):
        logging.info("begin sending IHU to %d neighbourgs" % len(self.s_n)) 

        for node in chain(self.u_n.values(), self.s_n.values()):
            node.add_tlv( Msg.IHU,  IHU(node._id))
    
    def check_neighbourgs(self):
        logging.info("checking if there is enought neighbours")

        if len(self.p_n) < 5 and self.s_n:
            logging.info("not enought neighbours, requesting others")
            node = random.choice( list(self.s_n.values()))
            node.add_tlv(Msg.NR, NeighbourgRequest()) 
    
    def update_data(self):
        logging.info("updating data")

        for id_data  in self.owned_data:
            seqno, data, last_update = self.data[id_data]

            self.data[id_data] = (seqno+1, data, time())
            self.tasks.appendleft( (Task.flood, (id_data, seqno+1, data)) )  

    def prune_data(self):
        del_keys = []
        for id_data, (seqno, data, last_update) in self.data.items():
            if last_update + 35*60 < time() and (id_data not in self.owned_data):
                del_keys.append(id_data)

        logging.info("pruning %d outdated data" % len(del_keys))

        for key in del_keys:
            del self.data[key]

        for node in self.s_n.values():
            for key in del_keys:
                if key in node.data:
                    del node.data[key]

    def register_flood(self, id_data, seqno_data, data):
        if id_data in self.floods:
            logging.debug("id data already in floods, this flood will be postpone")
            fl = self.floods[id_data]
            if fl.seqno < seqno_data:
                logging.info("stop flooding %s with seqno=%d and preapring %d" % (hex(id_data), fl.seqno, seqno_data))
                #we seed new content
                del self.floods[id_data]
                self.tasks.appendleft( (Task.flood, args) )
            else:
                logging.debug("already flooding more recent content")
        else:
            logging.info("begin flooding (%s, %d)" % (hex(id_data), seqno_data))
            self.floods[id_data]=Flood(id_data, seqno_data, data)

    def prune_neighbourgs(self):
        logging.info("pruning neighbourgs")

        for node in list(self.u_n.values()):
            if node.last_paquet + 100 < time():
                del self.u_n[node._id]
        for node in list(self.s_n.values()):
            if node.last_paquet + 150 < time() or node.last_ihu + 300 < time():
                del self.s_n[node._id]
    
    def refresh_ihm(self):
       os.system('clear')
       
       title = "Node id: %s, Uptime: %ds" % (hex(self.id), int(time()-self.starttime))
       print( center(title) )
       print( center(underline(title)) )
       print( "\n")
      
       for name, htbl in [("Symetrical", self.s_n), 
               ("Unidirectionnal",self.u_n), ("Potential", self.p_n)]:
            title = "%s neighbourgs:" % name

            print( title )
            print( underline(title) )

            n_data = " "*9 + "Id" + " "*9 + " " + " "*16+ "Ip" + " "*17
            for node in htbl.values():
                l_p = int(time()-node.last_paquet) if node.last_paquet >= 0 else -1 
                l_i = int(time()-node.last_ihu) if node.last_ihu >= 0 else -1 
                n_data = "%s\n  %s  %s:%d  %d  %d" % (n_data, hex(node._id),
                        node.addr[0], node.addr[1], l_p, l_i)
            print(n_data)

       title = "Data :"
       print(title)
       print( underline(title))

       b_data = " "*9 + "Id" + " "*9 + " " + "Seqno Len Time Owned "
       for _id, (seqno, data, last_update) in self.data.items():
           b_data = "%s\n  %s  %d %d %d %s |%s|" % (
                   b_data, hex(_id), seqno, len(data),
                   (int(time()-last_update) if last_update >=0 else -1), 
                   repr(_id in self.owned_data), extract_data(data))
       print( b_data )

    def process_task(self):#il faut modifier self.tasks tl (pointeur de fct, args)
        if not self.tasks:
            return

        _type, args = self.tasks.pop()
        logging.debug("begin process_task %s " % str(_type))
        
        if _type == Task.contact_u_n:
            self.contact_u_n()
        elif _type == Task.ihu_s_n:
            self.ihu_s_n()
        elif _type == Task.check_neighborgs:
            self.check_neighbourgs()
        elif _type == Task.update_data:
            self.update_data()
        elif _type == Task.prune_data:
            self.prune_data()
        elif _type == Task.flood:
            id_data, seqno_data, data = args
            self.register_flood(id_data, seqno_data, data)
        elif _type == Task.prune_neighborgs:
            self.prune_neighbourgs()
        elif _type == Task.refresh_ihm:
            self.refresh_ihm()
            
### Recv 
    def update_node(self, node_id, addr):
        #maintenance de la liste des paquets
        if (node_id not in self.u_n) and (node_id not in self.s_n):
            if node_id in self.p_n:
                node = self.p_n[node_id]
                del self.p_n[node_id]
            else:
                node = Node(node_id, addr, time(), -1)

            logging.info("%s added to unidirectionnal neighbours" % node)
            self.u_n[node_id] = node
            node.add_tlv(Msg.IHU, IHU(node_id))#première connection du coup on envoit un IHU
        elif node_id in self.u_n:
            node = self.u_n[node_id]
        elif node_id in self.s_n:    
            node = self.s_n[node_id]
        
        node.addr = addr
        node.last_paquet = time()
        
        return node
    
    def recv_IHU(self, node, id_dest):
        if id_dest != self.id:
            return

        logging.info("Received IHU from %s and processing" % node)
        if node._id in self.u_n:
            del self.u_n[node._id]
        elif node._id in self.p_n:
            del self.p_n[node._id]

        node.last_ihu = node.last_paquet
        self.s_n[node._id] = node
        
        for id_data, (seqno_data, data,_) in self.data.items():
            self.tasks.appendleft( (Task.flood, (id_data, seqno_data, data)) ) 

    def recv_neighbourgs_request(self, node):     
        logging.info("Received NeighbourgRequest and processing")

        #filter lui même
        #7 car 7*26<250 ie tiens dans un tlv et comme ça on peut perdre 2 voisins avant la prochaine requête
        ids = random.sample(list(self.s_n.keys()), min(7, len(self.s_n)))
        ids = filter(lambda x: x!=node._id, ids)
        node.add_tlv(Msg.N, Neighbourg([(i,self.s_n[i]) for i in ids]))

    def recv_neighbourgs(self, node, neighbourgs):
        logging.info("Received Neighbourg and processing")

        for (id0, addr0) in neighbourgs: 
            if id0 == self.id:
                continue
            elif id0 in self.p_n or id0 in self.u_n or id0 in self.s_n:
                #on prefère faire confiance à nos propre données
                continue
            else:     
                self.p_n[id0] = Node(id0, addr0, time())

    def recv_data(self, node, id_data, seqno_data, data_pub):
        logging.info("Received Data (%s,%d) from %s" % (hex(id_data), seqno_data, node))
                
        node.add_tlv(Msg.IHave, IHave(id_data, seqno_data))
        
        if id_data in self.owned_data:#on protège nos données
            return

        if id_data in node.data:
            node.data[id_data] = max(seqno_data, node.data[id_data])
        else:
            node.data[id_data] = seqno_data

        if id_data in self.data:
            if self.data[id_data][0] < seqno_data:
                self.data[id_data] = (seqno_data, data_pub, time())
                self.tasks.appendleft( (Task.flood, (id_data, seqno_data, data_pub)) )  
        else:
             self.data[id_data] = (seqno_data, data_pub, time())
             self.tasks.appendleft( (Task.flood, (id_data, seqno_data, data_pub)) )  
    
    def recv_IHave(self, node, id_data, seqno_data):
        logging.info("Received IHave (%s,%d)" % (hex(id_data), seqno_data))
        if id_data in node.data:
            node.data[id_data] = max(seqno_data, node.data[id_data])
        else:
            node.data[id_data] = seqno_data


    def process_paquet(self, data, addr):
        if not data:
            return 

        _id, tlvs = to_tlvs(data)
        node = self.update_node(_id, addr)
        if not tlvs:
            return None
        
        for (_type, args) in tlvs:
            if _type == Msg.Pad1 or _type == Msg.PadN:
                pass
            elif _type == Msg.IHU:
                self.recv_IHU(node, args)
            elif _type == Msg.NR:
                self.recv_neighbourgs_request(node) 
            elif _type == Msg.N:
                self.recv_neighbourgs(node, args)
            elif _type == Msg.Data:
                id_data, seqno_data, data_pub = args
                self.recv_data(node, id_data, seqno_data, data_pub)
            elif _type == Msg.IHave:
                id_data, seqno_data= args
                self.recv_IHave(node, id_data, seqno_data)

    def process_ballot(self, data, addr):
        _t, args = parse_ballot(data)
        if _t == Trame.Insert:
            data_id, data = args
            logging.info("Trame insert for %s" % hex(data_id))

            self.owned_data.add(data_id)
            if data_id in self.data:
                seqno = self.data[data_id][0]+1
            else:
                seqno = 0

            self.data[data_id] = (seqno, data, time())
            self.tasks.appendleft( (Task.flood, (data_id, seqno, data)) ) 
        elif _t == Trame.Delete:
            data_id = args
            logging.info("Trame delete for %s" % hex(data_id))

            if data_id not in self.data:
                return

            self.owned_data.discard(data_id)
            self.data[data_id]=(self.data[data_id][0],self.data[data_id][1],-1)
            self.prune_data()

    def process_recv(self, data, addr):
        if not data:
            return 

        if data[0] == 57:
            self.process_paquet(data, addr)
        elif data[0] == 58:
            self.process_ballot(data, addr)

    def proccess_floods(self):
        logging.debug("begin process floods")
        del_keys = []
        for fl in self.floods.values():
            if fl.dead():
                del_keys.append(fl._id)

            if not fl.ready() or fl.dead():
                continue

            fl.run()
            end = True
            for node in filter(lambda node:fl.concerning(node), self.s_n.values()):
                end = False
                node.add_tlv(Msg.Data, Data(fl._id, fl.seqno, fl.data))
                logging.info("flooding %s,%d to %s" %(hex(fl._id), fl.seqno, node))

            if end:        
                del_keys.append( fl._id)

        for key in del_keys:
            del self.floods[key]

    def run(self):
        """
        main loop
        """
        try:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
            self.sock.bind((self.ip, self.port ))
            self.sock.settimeout(TIMEOUT)
        except Exception as e:
            log_exc(e)
            return False 

        logging.info("socket init (%s,%d): success!" % (self.ip, self.port))

        self.scheduler.start()

        self.starttime = time()

        while True:
            try:
                self.process_send()

                try:
                    data, addr=self.sock.recvfrom(PAQUET_MAX_LEN)
                    self.process_recv( data, addr )
                except socket.timeout:
                    pass
                
                
                self.process_task()
                self.proccess_floods() #probablement trop de priorité donnée au floods
            except Exception as e:
                log_exc(e)  
