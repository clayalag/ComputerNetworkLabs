from random import seed
from random import randint
from bitstring import Bits
import os.path
import socket
import random

def channel_biterror(hexastr1):
#espera una cadena hexadecimal con un header de 32 bits (16 hex chars)
#devuelve la cadena con algun error
    hexastr=(Bits(hex=hexastr1))
    bitsstr=(hexastr.bin)
    max_errores=2
    nerr=0 #pueden cambiar para aumentar o disminuir los errores
    for i in range(max_errores):
        nerr+=randint(0,1)
    #print(nerr) #descomentar para debug
    for j in range(nerr):
        final=""
        lugar_hex = randint(0,len(bitsstr)-1)
        #print(lugar_hex)#descomentar para debug
        l=0
        for a in bitsstr:
            if(l==lugar_hex):
                if(a=="1"):
                    final+="0"
                else:
                    final+="1"
            else:
                final+=a
            l+=1
        bitsstr=final
    hexout=""
    #print('bitsstr type 2: ', type(bitsstr))
    veces=int(len(bitsstr)/8)
    for b in range(0,veces):
        hexout+="%02x" % int(bitsstr[b*8:(b+1)*8], 2)
    return hexout
    
def checksum(header, size):
    ptr = 0
    cksum=""
    hexastr=(Bits(hex=header))
    bitsstr=(hexastr.bin)
    #print('bitsstr: ', bitsstr)
    for b in range(0,int(size/8)):
        cksum += "%02x" % int(bitsstr[b*8:(b+1)*8], 2)
    #print('CKSUM hex: ', cksum)
    #suma en pares de 2 bytes.
    cksum = int(cksum,16)
    #print('Cksum 1: ', cksum)
    cksum = (cksum >> 16) + (cksum & 0xffff)
    #print('Cksum 2: ', cksum)
    cksum += (cksum >> 16)
    #print('Cksum 3: ', cksum)
    
    return (~cksum) & 0xFFFF

def process_cksumpkt(pktcksum, size):
    while size != 16:
        pktcksum = '0' + pktcksum
        size = len(pktcksum)
    return pktcksum

    
def isNak(msg):
    obejeto_en_bytes = bytes.fromhex(msg[8:16])
    NAK = obejeto_en_bytes.decode("utf-8", "replace")
    for i in range(len(NAK)):
        if NAK[i] == '1':
            return True
    return False
        
def isACK(msg, previous_seq):
    obejeto_en_bytes = bytes.fromhex(msg[:8])
    ACK = obejeto_en_bytes.decode("utf-8", "replace")
    objetoenbytes = bytes_object = bytes.fromhex(msg[16:32])
    pkt_seq_num = objetoenbytes.decode("utf-8", "replace")
    pseq_flag = False
    if previous_seq == pkt_seq_num:
        pseq_flag = True
    for i in range(len(ACK)):
        if ACK[i] == '1':
            return True
    return False
            

def create_cksum():
    largo = 0
    cksum = ''
    while largo != 16:
        cksum += '0'
        largo = len(cksum)
    return cksum

def make_pkt(segHeader, data, cksum):
    #print('Cksum value: ', pktcksum)
    if len(pktcksum) < 16:
        cksum = process_cksumpkt(cksum, len(cksum))
        #print('Packet cksum: ',pktcksum)
    pktheader = segHeader + cksum
    hexaPktHeader=pktheader.encode('utf-8').hex()
    hexPktHeader = hexaPktHeader + hexastr1
    salida=channel_biterror(hexPktHeader)
    #print('Esto es salida: ',salida)
    #print(type(salida))
    return salida
    
def rcv_pkt(msg):
    obejeto_en_bytes = bytes.fromhex(msg[:])
    mensaje = obejeto_en_bytes.decode("utf-8", "replace")
    #print('Mensaje recibido: ',mensaje)
    obejeto_en_bytes = bytes.fromhex(msg[:8])
    ACK = obejeto_en_bytes.decode("utf-8", "replace")
    obejeto_en_bytes = bytes.fromhex(msg[8:16])
    NAK = obejeto_en_bytes.decode("utf-8", "replace")
    objetoenbytes = bytes_object = bytes.fromhex(msg[16:32])
    pkt_seq_num = objetoenbytes.decode("utf-8", "replace")
    objetoenbytes = bytes_object = bytes.fromhex(msg[32:64])
    pkt_cksum = objetoenbytes.decode("utf-8", "replace")
    bytes_object = bytes.fromhex(msg[64:])
    pkt_data = bytes_object.decode("utf-8", "replace")
    return ACK, NAK, pkt_seq_num, pkt_cksum, pkt_data

def search(cksumlist, val):
    for i in range(len(cksumlist)):
        if cksumlist[i] == val:
            return True
    return False
    
def corrupt(msg):
    pktcksum = checksum(msg,len(pkt))
    pktcksum = "{0:b}".format(pktcksum)
    return search(pktcksum,'1')
    

if __name__ == '__main__':
    host = 'localhost'
    sender_port = 8001
    receiver_port = 8000
    ACK = '0000'
    #NAK = '0000'
    previous_seq = ''
    sender_address = (host, sender_port)
    receiver_address = (host, receiver_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(sender_address)
    
    archivo="test.txt"
    pedazos=100
    if(os.path.isfile(archivo)):
        f = open(archivo,"r")
        for i in range(0,os.path.getsize(archivo) ,pedazos):
            seq_num = random.getrandbits(8)
            #print('Raw seq num: ', seq_num)
            seq_num = "{0:b}".format(seq_num)
            #print('Seq num: ',seq_num)
            cksum = create_cksum()
            seg_header = ACK + '0000' + seq_num + cksum
            linea = f.read(pedazos)
            hexastr1=linea.encode('utf-8').hex()
            hexaHeader=seg_header.encode('utf-8').hex()
            #print('Pkt: ',hexaHeader+hexastr1)
            pkt = hexaHeader+hexastr1
            pktcksum = checksum(pkt,len(pkt))
            pktcksum = "{0:b}".format(pktcksum)
            print('Pkt cksum: ', pktcksum)
            sndpkt = make_pkt(ACK + '0000' + seq_num, hexastr1,pktcksum)

            sock.sendto(sndpkt.encode(),receiver_address)
            bytes_object = bytes.fromhex(sndpkt[:])
            ascii_string = bytes_object.decode("utf-8", "replace")
            print('ASCII-STRING: ',ascii_string)
            msg = sock.recv(1024).decode()
            while msg and (corrupt(msg) or isNak(msg, previous_seq)):
                print('Resending')
                sndpkt = make_pkt(ACK + '0000' + seq_num, hexastr1,pktcksum)
                sock.sendto(sndpkt.encode(),receiver_address)
                msg = sock.recv(1024).decode()
            if msg and (not corrupt(msg) and isACK(msg, previous_seq)):
                print('We good')
            previous_seq = seq_num
                
