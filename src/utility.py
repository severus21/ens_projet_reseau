from ipaddress import *



def ip_byte_to_string (ip):
    x = ip_address(ip)
    if x.ipv4_mapped !=None :
        return str (x.ipv4_mapped)
    else :
        return str(x)
    
def ip_string_to_byte (ip):
    x = ip_address(ip)
    if x.version == 4:
        return (IPv6Address ( "::FFFF:" + ip)).packed
    else:
        return x.packed

print(ip_byte_to_string(ip_string_to_byte("120.156.24.30")))
