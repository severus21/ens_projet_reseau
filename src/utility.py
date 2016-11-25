import os, sys, traceback
import logging

from ipaddress import *

def to_bytes(num, n_bytes):
    return (num).to_bytes(n_bytes, byteorder='big')

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

def log_exc(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    d = "\n".join(  traceback.format_exception(exc_type, exc_obj, 
        exc_tb))
    logging.warning("""error unknow in main loop %s in %s at line %d :
    %s %s""" % (str(exc_type), str(fname), exc_tb.tb_lineno, str(e), 
    d))
