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
    veces=int(len(bitsstr)/8)
    for b in range(0,veces):
        hexout+="%02x" % int(bitsstr[b*8:(b+1)*8], 2)
    return hexout

def checksum(header, size, cksum):
    ptr = 0
    cksumbitsstr=""
    hexastr=(Bits(hex=header))
    bitsstr=(hexastr.bin)
    #cksumstr=(Bits(hex=cksum))
    #cksumbitsstr=(cksumstr.bin)
    #print('bitsstr: ', bitsstr)
    for b in range(0,int(size/8)):
        cksumbitsstr += "%02x" % int(bitsstr[b*8:(b+1)*8], 2)
    #print('CKSUM: ', cksum)
    #suma en pares de 2 bytes.
    #print('Cksum before int: ', cksum)
    cksum = int(cksumbitsstr,16)
    cksum = (cksum >> 16) + (cksum & 0xffff)
    cksum += (cksum >> 16)
    #print('Cksum 3: ', cksum)
    
    return (~cksum) & 0xFFFF
    
def search(cksumlist, val):
    for i in range(len(cksumlist)):
        if cksumlist[i] == val:
            return True
    return False
    
def extract_pkt(pkt):
    objetoenbytes = bytes_object = bytes.fromhex(pkt[:8])
    pktACK = objetoenbytes.decode("utf-8", "replace")
    #print('Cksum string: ',cksum_str)
    objetoenbytes = bytes_object = bytes.fromhex(pkt[8:16])
    pktNAK = objetoenbytes.decode("utf-8", "replace")
    objetoenbytes = bytes_object = bytes.fromhex(pkt[16:32])
    pkt_seq_num = objetoenbytes.decode("utf-8", "replace")
    objetoenbytes = bytes_object = bytes.fromhex(pkt[32:64])
    pktcksum = objetoenbytes.decode("utf-8", "replace")
    #print('Cksum string objeto: ',pktPseuHeader)
    bytes_object = bytes.fromhex(pkt[64:])
    pktData = bytes_object.decode("utf-8", "replace")
    #cksum_list = cksum_str.split()
    return pktACK, pktNAK, pkt_seq_num, pktcksum, pktData

if __name__ == '__main__':
    host = 'localhost'
    sender_port = 8001
    receiver_port = 8000
    sender_address = (host, sender_port)
    receiver_address = (host, receiver_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(receiver_address)
    while True:
        pkt, sender_address = sock.recvfrom(1024)
        pkt = pkt.decode()
        ACK, NAK, seq_num, cksum, data =extract_pkt(pkt)
        receivedcksum = cksum
        receivedcksum = receivedcksum.encode('utf-8').hex()
        pktcksum = checksum(pkt,len(pkt), receivedcksum)
        pktcksum = "{0:b}".format(pktcksum)
        print('Esto es cksum: ', pktcksum)
        
        if search(pktcksum,'1'):
            NAK = '1111'
            sndpkt = ACK + NAK + seq_num + cksum + data
            #print('Pkt to sender before channel_biterror: ', sndpkt)
            pktToSender = sndpkt.encode('utf-8').hex()
            pktToSender = channel_biterror(pktToSender)
            #print('Pkt to sender after channel_biterror: ', pktToSender)
            sock.sendto(pktToSender.encode(),sender_address)
        else:
            ACK = '1111'
            sndpkt = ACK + NAK + cksum + data
            pktToSender = sndpkt.encode('utf-8').hex()
            pktToSender = channel_biterror(pktToSender)
            print('Todo SUPER bien: ',sndpkt)
            #print(type(pktcksum))
            sock.sendto(pktToSender.encode(),sender_address)
