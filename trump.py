import logging

from src.engine import Engine

logging.basicConfig(
    #filename="trump.log", 
    format='''%(asctime)s  %(levelname)s  %(filename)s %(funcName)s %(lineno)d 
    %(message)s''', level=logging.DEBUG)

engine = Engine(ip='0.0.0.0', port=5123, bootstrap=[
    #(int("9474a7c5038fd2d5",16), ('2001:660:3301:9200::51c2:1b9b', 1212)), 
    (int("9474a7c5038fd2d5",16), ('81.194.27.155', 1212)), 
])
engine.run()
