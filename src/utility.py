from ipaddress import *

def ipv_2_ipv6(ip):
    x = ip_address(ip)
    if x.version == 4 and not x.ipv4_mapped:
        return  "::FFFF:" + ip
    else:
        return ip


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

def center(_str):
    k = int((80-len(_str))/2)
    return " "*k + _str + " "*k

def underline(_str):
    return "="*len(_str)
