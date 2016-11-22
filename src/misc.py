from enum import Enum

PAQUET_MAX_LEN = 4096

class Msg(Enum):
    Pad1 = 1
    PadN = 2
    IHU = 3
    NR = 4 #Neighbour Request
    N = 5 #Neighbours
    Data = 6
    IHave = 7

class Task(Enum):
    #contact unidirectional neighborgs, each 30s
    contact_u_n = 1

    #send IHU to symetrical neighborgs, each 90s
    ihu_s_n = 2

    #check if there is enough neighborgs
    check_neighborgs = 3

    #update data, ie send data and incr seqno
    update_data = 4

    #check if there is data stagging, ie not update for 35min
    prune_data = 5

    #flood (id_datan seqno_data, data)
    flood = 6

    #each 100s prune u_n, 15Os s_netc
    prune_neighborgs = 7

    #each 1s refresh ihm
    refresh_ihm = 8
