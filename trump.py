import logging
import argparse

from src.engine import Engine

logging.basicConfig(
    filename="trump.log", 
    format='''%(asctime)s  %(levelname)s  %(filename)s %(funcName)s %(lineno)d 
    %(message)s''', level=logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument("-p", nargs='?', dest='p', default=None, type=int)
args = parser.parse_args()



engine = Engine(ip='::', port=args.p, bootstrap=[
    (int("9474a7c5038fd2d5",16), ('2001:660:3301:9200::51c2:1b9b', 1212)), 
   #(int("7d6d23263041e011",16), ('81.194.27.155', 1212)), 
])
engine.start()
