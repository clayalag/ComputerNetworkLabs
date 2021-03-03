import threading, time, select, json, socket
from math import inf
from binascii import hexlify
import json


#G=[[0,2,5,1,inf],
 #  [2,0,3,2,inf],
  # [5,3,0,3,1],
   #[1,2,3,0,1],
  # [inf,inf,1,1,0]]

G=[[0,5,1,inf],
    [5,0,3,1],
    [1,3,0,1],
    [inf,1,1,0]]
#
#G=[[0,2,5,1,inf,inf],
#  [2,0,3,2,inf,inf],
#  [5,3,0,3,1,5],
#  [1,2,3,0,1,inf],
#  [inf,inf,1,1,0,2],
#  [inf,inf,5,inf,2,0]
#  ]

# G=[[  0,  5,inf,inf,  2,inf,inf,inf,inf],
#    [  5,  0,  7,inf,  2,  3,inf,inf,inf],
#    [inf,  7,  0,  8,inf,  2,  5,  7,inf],
#    [inf,inf,  8,  0,inf,inf,inf,  3,  4],
#    [  2,  2,inf,inf,  0,  2,  9,inf,inf],
#    [inf,  3,  2,inf,  2,  0,  6,inf,inf],
#    [inf,inf,  5,inf,  9,  6,  0,  2,inf],
#    [inf,inf,  7,  3,inf,inf,  2,  0,inf],
#    [inf,inf,inf,  4,inf,inf,inf,inf,  0]
#    ]

#G=[[0,2,7],
 #   [2,0,1],
  #  [7,1,0]]
   
L=len(G)

#funcion que construye D y P recibe el vector de distancia inicial d y el nodo
#debe devolver una lista de dos dimensiones D que contiene las distancias entre cada nodo y
#el vector P que contiene el nodo por el cual se debe salir para llegar al nodo deseado
def construyeDP(d, nodo):
    #print("MandO_0: ", d)
    #print("MandO_1: ", nodo)
    D = [[inf]*len(d)]*len(d) # crea matriz D
    D[nodo] = d
    #print("MandO_2A: ", D)
    P = []
    for i in range(len(d)):
        if D[nodo][i] != inf:
            P.append(i) # tiene la info de ese vecino
        else:
            P.append(None)
    #print("MandO_2B: ", D)
    #print("MandO_3: ", P)
    return D, P
    
#funcion que hace update a D y a P con la informacion recibida y se verifica si cambio
#recibe el D y P de este nodo y el D (aqui se denota V) recibido por el vecino v
#debe devolver el D y el P revisado y la variable booleana "cambio" si D cambio'
# bellman-ford
def revisaInfo(D,V,nodo,v,P):
    print('Matriz D: ', D)
    print('Forwarding Table P: ', P)
    print("Nodo: ", nodo)
    print('Matriz V: ', V)
    print('vecino: ', v)
    cambio = []
    for i in range(len(D)):
        if D[nodo][v] + V[v][i] < D[nodo][i]:
            D[nodo][i] = D[nodo][v] + V[v][i]
            P[i] = v
            cambio = True
            print('Prueba CAMBIO 1: ', D, P)
        if D[nodo][i] == inf and V[v][i]:
            D[nodo][i] = D[nodo][v] + V[v][i]
            P[i] = v
            cambio = True
            print('Prueba CAMBIO 2: ', D, P)
        D[v][b] = V[v][b]
    print('Matriz D con update del vecino: ', D)
    return D, P, cambio

#funcion que define los vecinos del nodo basado en el vector de distancia inicial
#recibe el vector de distancia inicial d y el nodo
#debe devolver una lista con los vecinos
def set_vecinos(d,nodo):
    vecinos = []
    for i in range(len(d)):
        if i != nodo and d[i] != inf:
            vecinos.append(i)
        
    return vecinos

#funcion que envia el mensaje en bytearray a los vecinos
#recibe info_dar que es el mensaje en bytearray, la lista de vecinos y el puerto base
#no devuelve nada
def envia_vecinos(vecinos,info_dar,puerto_base):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for i in vecinos:
        sock.sendto(info_dar, ('localhost', puerto_base+i))
    sock.close()
    return None

#funcion que procesa el mensaje recibido que contiene el D y el identificador del vecino
#recibe el mensaje recibido en forma bytearray
#devuelve el D y el identificador del vecino
def procesa_mensaje(infoNueva):
    info = tuple(json.loads(infoNueva.decode()))
    V = info[1]
    v = info[0]
    return V, v

#funcion que crea el mensaje a enviar a los vecinos
#recibe el nodo y la lista D
#devuelve el mensaje en bytearray para poder enviarlo por los sockets
def crea_mensaje(nodo,D):
    data = (nodo, D)
    dump = json.dumps(data).encode()
    info_dar = dump
    return info_dar

#funcion que ejecuta cada thread
def arranca_nodo(nodo, d):
    L=len(d)                            #la cantidad de nodos
    esperar_escuchando_por_vecinos=2      #segundos que el socket espera por los mensajes de sus vecinos
    espera_ciclos=int(L/2)                 #iteraciones esperando por vecinos antes de terminar
    puerto_base=12000                     #numero de puerto base
    puerto=puerto_base+nodo             #los puertos de cada nodo
    serverSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #socket udp donde escucha el thread
    serverSocket.bind(('',puerto))        #se fija con el puerto
    D , P = construyeDP(d, nodo)         #llamada a funcion que construye D y P basado en el vector de distancia inicial el nodo
    print(str(nodo)+"D: ", end="")
    print(D)
    print(str(nodo)+"P: ", end="")
    print(P)
    vecinos = set_vecinos(d,nodo)        #llamada a funcion que define los vecinos basado en el vector de distancia inicial el nodo
    #print(f'Vecinos de nodo {nodo}: {vecinos}')
    conteo=0;                             #se inicializa el conteo de iteraciones que se espera por mensajes de vecinos
    cambio=True                         #se inicializa camibo a true para que pueda empezar el ciclo
    while 1:
        if cambio:                       #si hubo cambio en D
            #aqui nos preparamos para enviar a los vecinos
            info_dar=crea_mensaje(nodo,D) #funcion que crea el mensaje que vamos a enviarle a nuestros vecinos
            envia_vecinos(vecinos,info_dar,puerto_base)#funcion que envia mensaje a los vecinos
        #aqui nos preparamos para escuchar a los vecinos
        infoNueva=None                  #se inicializa la variable que va a recibir el mensaje de los vecinos
        ready = select.select([serverSocket], [], [], esperar_escuchando_por_vecinos) #la funcion select espera que este ready el serverSocket
        #ademas permite anhadir tiempo de espera
        if ready[0]:                       #si antes de que esperar_por_vecinos se venza llega algo se le asigna a ready
            conteo=0;                     #inicializamos el conteo de iteraciones
            infoNueva, address = serverSocket.recvfrom(2048)  #el socket recibiendo de los vecinos
            V, v = procesa_mensaje(infoNueva) #llamada a funcion que extrae la informacion recibida
            D, P, cambio=revisaInfo(D,V,nodo,int(v),P) #se hace update a D y a P con la informacion recibida y se verifica si cambio
            if cambio:
                print(str(nodo)+"D: ", end="")
                print(D)
                print(str(nodo)+"P: ", end="")
                print(P)
        if infoNueva is None:             #si despues de esperar escuchando por vecinos no llega nada
            if conteo<espera_ciclos:     #se verifica la cantidad de iteraciones
                conteo+=1
            else:                        #si se completaron se imprime la D y la P resultante
                print(str(nodo)+"D..: ", end="")
                print(D)
                print(str(nodo)+"P..: ", end="")
                print(P)
                break
try:
    #crea los threads y los activa para ejecutar la funcion arranca_nodo con args (i,G[i])
    #
    threads = []
    for i in range(L):
        t = threading.Thread(target=arranca_nodo, args=(i,G[i])) #crea los threads para ejecutar la funcion arranca_nodo con args (i,G[i])
        threads.append(t) #pone los threads en una lista para luego asociarlos al main thread con join
        t.start()    #arranca los threads

except:
    print("Error: generando threads")

for th in threads:
    th.join()     #asocia los thread al main thread para que main espero por los threads

print("Acabamos")

