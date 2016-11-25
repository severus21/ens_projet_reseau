import unittest
import random
import string

from src.paquet import *
from src.utility import *

class TestTlv(unittest.TestCase):
    def test_pad1(self):
        tlv = to_bytes(0, 1)
        self.assertEqual(tlv, Pad1())
        self.assertEqual(len(tlv), 1)

    def test_padn(self):     
        for n in range(256):    
            tlv = to_bytes(1, 1)
            tlv += to_bytes(n, 1)
            tlv += to_bytes(0, n)
            self.assertEqual(tlv, PadN(n))
            self.assertEqual(len(tlv), n+2)
            self.assertTrue(len(tlv)<258)

    def test_ihu(self):
        _id = random.randint(0, 2**64)

        tlv = to_bytes(2, 1)
        tlv += to_bytes(8, 1)
        tlv += to_bytes(_id, 8)

        self.assertEqual(tlv, IHU(_id))
        self.assertEqual(len(tlv), 10)

    def test_nr(self):
        tlv = to_bytes(3, 1)
        tlv += to_bytes(0, 1)

        self.assertEqual(tlv, NeighbourgRequest())
        self.assertEqual(len(tlv), 2)
   
    def test_n(self):
        _id, port = random.randint(0,2**64), 1212
        ip = "80.214.19.115"
        
        for n in range(9):
            tlv = to_bytes(4, 1)
            m =(8-(n*26)%8 if (n*26)%8!=0 else 0)
            tlv += to_bytes(n*26+m, 1)
            l = []
            for i in range(n):
                tlv += to_bytes(_id, 8) + ip_string_to_byte(ip) + to_bytes(port,2)
                l.append( (_id,(ip, port)) )
            tlv += to_bytes(0, m)

            self.assertEqual(tlv, Neighbourg(l), "%s %s " % (bytes(tlv), bytes(Neighbourg(l))))
            self.assertEqual(len(tlv), 2 + 26*n+m)
            self.assertTrue(len(tlv)<258)

    def test_data(self):
        _id = random.randint(0, 2**64)
        for n in range(256-12):
            tlv = to_bytes(5,1)
            tlv += to_bytes(n+12,1)
            tlv += to_bytes(0,4)
            tlv += to_bytes(_id,8)
            data = to_bytes(random.getrandbits(n), n) if n else b''
            tlv += data
            
            self.assertEqual(tlv, Data(_id, 0, data))
            self.assertEqual(len(tlv), n+14)
            self.assertTrue(len(tlv)<258)

    def test_ihave(self):
        _id = random.randint(0,2**64)
        tlv = to_bytes(6, 1)
        tlv += to_bytes(12,1)
        tlv += to_bytes(0, 4)
        tlv += to_bytes(_id,8)

        self.assertEqual(tlv, IHave(_id, 0))
        self.assertEqual(len(tlv), 14)

    def test_data_str(self):
        for n in range(256):
            _str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
            tlv = to_bytes(32,1)
            tlv += to_bytes(n, 1)
            tlv += _str.encode()
        
            self.assertEqual(tlv, Data_str(_str))
            self.assertEqual(len(tlv), n+2)
            self.assertTrue(len(tlv) < 258)
            
class TestPaquet(unittest.TestCase):
    def setUp(self):
        self.id = random.randint(0,2**64)
        self.N = 20
        self.data_id = random.randint(0,2**64)
        self.data_seqno = random.randint(0,2**16)
        self.data_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(60))
        self.data_bytes = to_bytes(random.getrandbits(50),50)
        
        self.tlvs = [Hello(), Pad1(), PadN(self.N), 
                IHU(self.id), NeighbourgRequest(),
                Neighbourg([]),Data(self.data_id, self.data_seqno, self.data_bytes),
                Data_str(self.data_str), IHave(self.data_id, self.data_seqno),
                Data(self.data_id, self.data_seqno, Data_str(self.data_str))]


        self.buff = to_bytes(57, 1) + to_bytes(0, 1)
    
    def tearDown(self):
        self.buff = b''

    def test_hello(self):
        for tlv in self.tlvs:        
            buff = self.buff+to_bytes(len(tlv),2)+to_bytes(self.id,8)+tlv 

            self.assertEqual(buff, make_paquet(self.id, [tlv]))
    
    def test_many(self):
        for k in range(50):
            tlvs = [ random.choice(self.tlvs) for k in range(15) ]
            buff = self.buff + to_bytes(sum(map(len,tlvs)),2)
            buff += to_bytes(self.id,8) + b''.join(tlvs)

            self.assertEqual(buff, make_paquet(self.id, tlvs))
    

if __name__ == '__main__':
    unittest.main()
