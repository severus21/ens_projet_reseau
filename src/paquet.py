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
    body = b''
    for (id, (ip, port)) in l :
        body += id+ip+port
    n = len(body)
    if n % 8 !=0:
        body += (0).to_bytes(8-n%8, byteorder = 'big')
        n+= 8-n%8
    type = (4).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + body
     
def Data (id, seqno, data):
    seqno =(seqno).to_bytes(4, byteorder = 'big')
    n = len(seqno)+len(id)+len(data)
    type = (5).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + seqno +id +data
     
def IHave(id,seqno):
    seqno =(seqno).to_bytes(4, byteorder = 'big')
    n = len(seqno)+len(id)
    type = (6).to_bytes(1, byteorder = 'big')
    length = n.to_bytes(1, byteorder = 'big')
    return type + length + seqno +id 


def make_paquet (self_id, l):
    body = b''
    for tlv in l :
        body += tlv
    magic = (57).to_bytes(1, byteorder = 'big')
    version = (0).to_bytes(1, byteorder = 'big')
    n = len(body)
    length = n.to_bytes(2, byteorder = 'big')
    return magic + version + length + self_id + body
 
   
def to_one_tlv (paquet, i):
    type = paquet[i]
    if (type == 0):  
        return (type+1,None), i+1
    if (type == 1) or (type == 3): 
        length = paquet[i+1]
        return (type+1,None), i + 2 + length
    elif type == 2:
        length = paquet[i+1]
        id = paquet[i+2:i+10]
        return (type+1, id),i+2+length
    elif type == 4:
        length = paquet[i+1]
        j = i+2
        l = []
        while (j < i+2+length-7):
            id = paquet[j:j+8]
            ip = paquet[j+8:j+24]
            port = paquet[j+24:j+26]
            j = j+26
            l.append((id,(ip,port)))
        return (type +1, l), i+2+length 
        
    elif type == 5:
        length = paquet[i+1]-12
        seqno = paquet[i+2:i+6]
        id = paquet[i+6:i+14]
        data = paquet[i+14:i+14+length]
        return (type + 1, (id, seqno, data)), i+14+length
    elif type == 6:
        length = paquet[i+1]
        seqno = paquet[i+2:i+6]
        id = paquet[i+6:i+14]
        return (type + 1, (id, seqno)), i+2+length
    else :
        length = paquet[i+1]
        return i+2 +length
    


def to_tlvs (paquet):
    n = int.from_bytes(paquet[2:4], byteorder = 'big')
    id = paquet[4:12]
    l = []
    i = 12
    while i < 12 + n:
        tlv,i = to_one_tlv(paquet, i)
        l.append(tlv)
    return (id, l)

