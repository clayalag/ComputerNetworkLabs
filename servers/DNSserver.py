import socket, os.path, time
import bitstring
from bitstring import BitArray

def byte2int(byteS, nbytes):
    numero=0
    for i in range(nbytes):
        numero+=byteS[i]*pow(256,nbytes-1-i)
    return numero

def Puntero(mensaje,loc,base_qs):
    puntero=[]
    puntero.append(loc&0x03)
    puntero.append(mensaje[base_qs+1])
    puntVal=byte2int(puntero,2)
    print("puntVal: "+str(puntVal))
    return puntVal

def sacaNombre(mensaje, next):
    nombre=" "
    loc=mensaje[next]
    if(loc==0):
        return nombre
    elif(loc & 0xc0):
        nextval = byte2int([(loc&0x03), mensaje[next+1]], 2)
        nombre+=sacaNombre(mensaje,nextval)
    else:
        return str(mensaje[next+1:next+1+loc]) + sacaNombre(mensaje,next+1+loc)
    return nombre

def getNext(mensaje,inicio):
    nextVal=inicio
    loc=mensaje[inicio]
    if(loc==0):
        return nextVal+1
    elif(loc & 0xc0):
        return nextVal+2
    else:
        return getNext(mensaje,nextVal+loc+1)


def parse_msg(mensaje):
    next:0
    print("HEADER")
    id = mensaje[0:2]
    print("id: "+str(byte2int(id,2)))
    bites=bin(mensaje[2])[2:]
    arrBits=bites.zfill(8)

    qr=arrBits[0]
    opcode=arrBits[1:5]
    aa=arrBits[5]
    tc=arrBits[6]
    rd=arrBits[7]

    bites=bin(mensaje[3])[2:]
    arrBits=bites.zfill(8)
    ra=arrBits[0]
    res1=arrBits[1]
    res2=arrBits[2]
    res3=arrBits[3]
    rcode=arrBits[4:8]

    flags=[]
    flags.append(qr)
    flags.append(opcode)
    flags.append(aa)
    flags.append(tc)
    flags.append(rd)
    flags.append(ra)
    flags.append(res1)
    flags.append(res2)
    flags.append(res3)
    flags.append(rcode)

    print("qr: "+str(qr), end=" ")
    print("opcode: "+str(opcode), end=" ")
    print("aa: "+str(aa), end=" ")
    print("tc: "+str(tc), end=" ")
    print("rd: "+str(rd), end=" ")
    print("ra: "+str(ra), end=" ")
    print("res1: "+str(res1), end=" ")
    print("res2: "+str(res2), end=" ")
    print("res3: "+str(res3), end=" ")
    print("rcode: "+str(rcode))

    total_qs=byte2int(mensaje[4:6],2)
    print("total_qs: "+str(total_qs))
    total_ans=byte2int(mensaje[6:8],2)
    print("total_ans: "+str(total_ans))
    entries_auth=byte2int(mensaje[8:10],2)
    print("entries_auth: "+str(entries_auth))
    entries_add = byte2int(mensaje[10:12],2)
    print("entries_add: "+str(entries_add))
    next=12
    print("QUERY")
    q_name=[]
    q_type=[]
    q_class=[]
    for i in range(total_qs):
        q_name.append(formatoNombre(sacaNombre(mensaje,next)))
        print("q_name"+str(i)+": "+str(q_name[i]))
        next=getNext(mensaje,next)
        q_type.append(mensaje[next:next+2])
        print("q_type"+str(i)+": "+str(byte2int(q_type[i],2)))
        q_class.append(mensaje[next+2:next+4])
        print("q_class"+str(i)+": "+str(byte2int(q_class[i],2)))
        next+=4
        print("qr: "+str(qr))
    if(int(qr) == 0):
        #print("entre a return")
        return [byte2int(id,2), flags, q_name[0], byte2int(q_type[0],2), byte2int(q_class[0],2)]
    print("RESPUESTAS")
    respuestaTotal=[]
    out=parseDataResp(mensaje,total_ans,next)
    next=out[0]
    respuestaTotal+=out[1]
    print("AUTORIDAD")
    out=parseDataResp(mensaje,entries_auth,next)
    next=out[0]
    respuestaTotal+=out[1]
    print("Adicional")
    out=parseDataResp(mensaje,entries_add,next)
    next = out[0]
    respuestaTotal+=out[1]
    return respuestaTotal

def formatoNombre(nombre):
    nombre=nombre.replace("b'", "")
    nombre=nombre.replace("'",".")
    return nombre

def parseDataResp(mensaje,total_ans,next):
    respuestas=[]
    r_name=[]
    r_type=[]
    r_class=[]
    r_ttl=[]
    r_data_l=[]
    r_data=[]
    for i in range(total_ans):
        r_name.append(formatoNombre(sacaNombre(mensaje,next)))
        print(str(r_name[i]), end=" ")
        next=getNext(mensaje,next)
        r_type.append(mensaje[next:next+2])
        print("type: "+str(byte2int(r_type[i],2)),end=" ")
        r_class.append(mensaje[next+2:next+4])
        print("class: "+str(byte2int(r_class[i],2)),end=" ")
        next+=4  # 1
        r_ttl.append(byte2int(mensaje[next:next+4],4))
        print("ttl: "+str(r_ttl[i]),end=" ")
        next+=4 # 1
        r_data_l.append(byte2int(mensaje[next:next+2],2))
        next+=2
        r_data.append(resuelveData(mensaje,byte2int(r_type[i],2),next,r_data_l[i]))
        print(str(r_data[i]))
        next+=r_data_l[i]
        if(byte2int(r_type[i],2)!=41):
            respuestas.append((r_name[i],byte2int(r_type[i],2),byte2int(r_class[i],2),r_ttl[i],r_data[i]))
    return (next, respuestas)

def sacaSoa(mensaje, inicio, largo):
    getNext(mensaje, inicio)
    name = formatoNombre(sacaNombre(mensaje, inicio))
    nextVal = getNext(mensaje, inicio)
    email = formatoNombre(sacaNombre(mensaje, nextVal))
    nextVal = getNext(mensaje, nextVal)
    sn = byte2int(mensaje[nextVal:nextVal+4], 4)
    ref = byte2int(mensaje[nextVal+4:nextVal+8],4)
    ret = byte2int(mensaje[nextVal+8:nextVal+12],4)
    exp = byte2int(mensaje[nextVal+12:nextVal+16],4)
    ttl = byte2int(mensaje[nextVal+16:nextVal+20],4)
    return name+" "+email+" "+str(sn)+" "+str(ref)+" "+str(ret)+" "+str(exp)+" "+str(ttl)
    
def formatoIpv6(numero):
    print(numero)
    numero = numero[2:]
    numero = numero.replace("0x",":")
    return numero
    
def resuelveData(mensaje, tipo, next, largo):
    if(tipo == 1):
        return (str((mensaje[next]))+"."+str(mensaje[next+1])+"."+str(mensaje[next+2])+"."+str(mensaje[next+3]))
    elif(tipo==2 or tipo==5 or tipo==12):
        return(formatoNombre(sacaNombre(mensaje,next)))
    elif(tipo == 6 or tipo == 11):
        return(sacaSoa(mensaje,next, largo))
    elif( tipo == 15):
        return(str(byte2int([mensaje[next],mensaje[next+1]],2))+ " " + formatoNombre(sacaNombre(mensaje, next+2)))
    elif(tipo == 28):
        return (formatoIpv6(hex(byte2int([mensaje[next],mensaje[next+1]],2)) + hex(byte2int([mensaje[next+2],mensaje[next+3]],2)) + hex(byte2int([mensaje[next+2],mensaje[next+3]],2)))) #mensaje[next+2]
    else:
        return(mensaje[next:next+largo])
        
def hexSoa(datosF):
    response = bytearray(0)
    arr = datosF.split()
    response += nombreHex[arr[0]]
    response += nombreHex[arr[1]]
    response += bytearray.fromhex(hex(int(arr[2]))[2:].zfill(8))
    response += bytearray.fromhex(hex(int(arr[3]))[2:].zfill(8))
    response += bytearray.fromhex(hex(int(arr[4]))[2:].zfill(8))
    response += bytearray.fromhex(hex(int(arr[5]))[2:].zfill(8))
    response += bytearray.fromhex(hex(int(arr[6]))[2:].zfill(8))
    return response
    
def ip4Hex(datosF):
    arr = datosF.split(".")
    response = bytearrey(0)
    for pet in arr:
        response += bytearray.fromhex(hex(int(pet))[2:].zfill(2))
    return response
    
def ip6Hex(datos):
    arr = datos.split(".")
    response = bytearray(0)
    for pet in arr:
        response += bytearray.fromhex(pet.zfill(4))
    return response
    
def nombreHex(nombreF):
    arr = nombreF.split(".")
    response = bytearray(0)
    for pet in arr:
        response += bytearray.fromhex(hex(len(pet))[2:].zfill(2))
        response += bytearray(pet, "ascii")
    return response
    
def procesaFlag(flag):
    response = bytearray(0)
    return bytearray.fromhex("8000")
    
def preparaResp(id, flags, nombre, tipo, clase, respEnCahche):
    response = bytearray.fromhex(hex(id)[2:].zfill(4))
    response += procesaFlag(flags)
    response += bytearray.fromhex("0001")
    response += bytearray.fromhex(hex(len(respEnCahche))[2:].zfill(4))
    response += bytearray.fromhex("0000")
    response += bytearray.fromhex("0000")
    response += nombreHex(nombre)
    response += bytearray.fromhex(hex(int(tipo))[2:].zfill(4))
    response += bytearray.fromhex(hex(int(clase))[2:].zfill(4))
    for respB in respEnCahche:
        response += respB
    return response
    
def respHex(datosF, tipo):
    response = bytearray(0)
    if(tipo == 15):
        arr = datosF.split()
        temp = bytearray.fromhex(hex(int(arr[0]))[2:].zfill(4))
        temp += nombreHex(arr[1])
        response += bytearray.fromhex(hex(len(temp))[2:].zfill(4)) + temp
    if(tipo == 6):
        temp = hexSoa(datosF)
        response += bytearray.fromhex(hex(len(temp))[2:].zfill(4)) + temp
    if(tipo == 2):
        temp = nombreHex(datosF)
        response += bytearray.fromhex(hex(len(temp))[2:].zfill(4)) + temp
    if(tipo == 1):
        response += bytearray.fromhex(hex(4)[2:].zfill(4)) + ip4Hex(datosF)
    if(tipo == 28):
        print("datos: " + datosF)
        temp = ip6Hex(datosF)
        response += bytearray.fromhex(hex(len(temp))[2:].zfill(4)) + temp
    return response
    
def buscaEnCahce(nombre, tipo):
    archBase = "DNS_cache_"
    archive = archBase+str(tipo)
    print(archive)
    print(nombre)
    arrResp = []
    updated = []
    if(os.path.isfile(archive)):
        f = open(archive, "r")
        for line in f:
            data = line.strip().split("\t")
            date = int(time.time())
            if(data[0] == nombre):
                ttlResp = int(data[2]) - date
                if(ttlResp > 0):
                    hexStr = nombreHex(nombre) + bytearray.fromhex(hex(int(tipo))[2:].zfill(4)) + bytearray.fromhex(hex(int(data[1]))[2:].zfill(4)) + bytearray.fromhex(hex(date)[2:].zfill(4))
                    arrResp.append(hexStr)
                    updated.append(line)
        f.close()
        if(len(arrResp) > 0):
            return arrResp
        else:
            return False
    else:
        return False
        
def guardaEnCache(paraCache):
    print("saving")
    archBase = "DNS_cache_"
    date = time.time()
    for line in paraCache:
        archive = archBase + str(line[1]) # 1
        if(not os.path.isfile(archive)):
            f = open(archive, "w+")
        else:
            f = open(archive, "a+")
        f.write(str(line[0]))
        f.write("\t")
        f.write(str(line[2]))
        f.write("\t")
        f.write(str(line[3] + int(date)))
        f.write("\t")
        f.write(str(line[4]))
        f.write("\n")
        print(line)
    f.close()

def limpiaCache():
    types = [1, 2, 6, 15, 28]
    for i in types:
        updated = []
        archive = "DNS_cache_"+str(i)
        if(os.path.isfile(archive)):
            f = open(archive, "r")
            for line in f:
                data = line.strip().split("\t")
                date = int(time.time())
                ttlResp = int(data[2])-date
                if(ttlResp > 0):
                    updated.append(line)
            f.close()
            f = open(archive, "w")
            for line in updated:
                f.write(line)
            f.close()

import socket
serverPort=12000
serverSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind(('',serverPort))
#ServerName='192.5.6.30'
ServerName='24.138.252.19'
#ServerName = '8.8.8.8'
DnsServerPort=53
print("Listo para recibir: " + str(serverPort))
while 1:
    DnsQuery, queryAddress = serverSocket.recvfrom(2048)
    print("query")
    print(DnsQuery)
    print(BitArray(DnsQuery))
    output = parse_msg(DnsQuery)
    id = output[0]
    flags = output[1]
    nombre = output[2]
    tipo = output[3]
    clase = output[4]
    print(output)
    respEnCahche = buscaEnCahce(nombre, tipo)
    if(respEnCahche):
        DnsResp = preparaResp(id, flags, nombre, tipo, clase, respEnCahche)
    #else:
    ClientSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ClientSocket.sendto(DnsQuery,(ServerName, DnsServerPort))
    DnsResp, serverAddress=ClientSocket.recvfrom(2048)
    ClientSocket.close()
    print("Response")
    print((DnsResp))
    #print(BitArray(DnsResp))
    paraCache=parse_msg(DnsResp)
    #paraCache = str(paraCache)
    guardaEnCache(paraCache)
    serverSocket.sendto(DnsResp,queryAddress)
    limpiaCache()
    print(DnsResp.hex())
    #serverSocket.sendto(DnsResp,queryAddress)
