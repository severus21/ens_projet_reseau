import logging
import socket
import pickle

from collections import deque
from random import getrandbits
from os.path import isdir
from time import time

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

        self.id = (getrandbits(64)).to_bytes(64, byteorder='big')
        self.seqno = 0

        #{"id": (seqno, donnée, date last update)} 
        self.data = {}
        
        #potential_neighbors, {'id': (date dernier paquet, date dernier IHU, ip, port)}
        self.n_p = {} 
        #unidirectional_neighbors, same
        self.u_n = {}
        #symmetrical_neighbors, same
        self.s_n = {}
        
        #list of pending tasks
        self.tasks = deque(maxlen=10**4)
        #message to be send not used
        self.msgs = dequet(maxlen=10**4)
        self.flood = False
        
   def load(self):
        pass

    def store(self):    
        pass

    def process_task(self):
    
    def process_recv(self, data, addr):
        

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
