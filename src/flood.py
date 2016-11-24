from time import time

class Flood:
    def __init__(self, _id, seqno, data, deadline=None, last_send=0): 
        self._id = _id
        self.seqno = seqno
        self.data = data
        self.deadline = deadline
        self.last_send = last_send
    
    def dead(self):
        return self.deadline and self.deadline<time()

    def ready(self):
        return self.last_send + 3 < time()

    def concerning(self, node):
        return self._id not in node.data or node.data[self._id]<self.seqno
      
    def run(self):
        if not self.deadline:
            self.deadline = time() + 11
            
        self.last_send = time()    
