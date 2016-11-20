def Pad1 () :
    return (0).to_bytes(1, byteorder = 'big') 
        
        
def PadN (mbz) :
    n = len(mbz)
    type = (1).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length+mbz
        
def IHU (id):
    n = len(id)
    type = (2).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + id
     
def Neighbourg_Request ():
    type = (3).to_bytes(1, byteorder = 'big')
    length = (0).to_bytes(1, byteorder = 'big')
    return type + length
     
def Neighbourg (l):
    n = 0
    body = b''
    for (id, (ip, port)) in l :
        body += id+ip+port
    n += len(body)
    n= n+ (8- (n % 8))  
    type = (4).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + body
     
def Data (id, seqno, data):
    seqno =(seqno).to_bytes(1, byteorder = 'big')
    n = len(seqno)+len(id)+len(data)
    type = (5).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + seqno +id +data
     
def IHave(id,seqno):
    seqno =(seqno).to_bytes(1, byteorder = 'big')
    n = len(seqno)+len(id)
    type = (6).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + sequo +id 


def make_paquet (self_id, l):
    body = b''
    for tlv in l :
        body += tlv
    magic = (57).to_bytes(1, byteorder = 'big')
    version = (0).to_bytes(1, byteorder = 'big')
    n = len(body)
    length = n.to_bytes(2, byteorder = 'big')
    return magic + version + length + self_id + body
