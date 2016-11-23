class Node:
    def __init__(self, _id, addr, last_paquet=-1, last_ihu=-1, data={}):
        """
        @param data{id_data:seqno max possédé par le noeud}
        """
        self._id = _id
        self.addr = addr
        self.last_paquet = last_paquet
        self.last_ihu = last_ihu
        self.data = data

