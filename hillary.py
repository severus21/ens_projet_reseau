import logging
import argparse
import socket

from src.paquet import Data_str 
from src.trame import *

logging.basicConfig(
    filename="hillary.log", 
    format='''%(asctime)s  %(levelname)s  %(filename)s %(funcName)s %(lineno)d 
    %(message)s''', level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument("-a", nargs='?', dest='action')#insert|delete
parser.add_argument("-host", nargs='?', dest='host') 
parser.add_argument("-p", nargs='?', dest='port', type=int)
parser.add_argument("-id", nargs='?', dest='data_id', type=lambda x:int(x,16))
parser.add_argument("-d", nargs='?', dest='data')
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.settimeout(1)

addr = (args.host, args.port)

if args.action.lower() == 'insert':
    sock.sendto(trame_insert(args.data_id, Data_str(args.data)),addr)
elif args.action.lower() == 'delete':    
    sock.sendto(trame_delete(args.data_id),addr)
