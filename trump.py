import logging
import argparse

from src.engine import Engine
from src.paquet import str_to_data 

logging.basicConfig(
    filename="trump.log", 
    format='''%(asctime)s  %(levelname)s  %(filename)s %(funcName)s %(lineno)d 
    %(message)s''', level=logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument("-p", nargs='?', dest='p', default=None, type=int)
parser.add_argument("-d", nargs='?', dest='d')
args = parser.parse_args()

engine = Engine(ip='::', port=args.p, bootstrap=[
    (int("d89b06b43762e43f",16), ('2001:660:3301:9200::51c2:1b9b', 1212)), 
   #(int("7d6d23263041e011",16), ('81.194.27.155', 1212)), 
], data= [str_to_data(args.d)] if args.d else [])
engine.start()
