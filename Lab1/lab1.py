#mpiexec -n 2 python lab1.py  #broj filozofa se tu odabire

from mpi4py import MPI
from time import sleep
from random import randint
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


#početna raspodjela vilica
#pocetna raspodjela susjeda
drzi_vilice = []
susjed = []
if rank==0:
    #[desna, lijeva]
    drzi_vilice = ["prljava","prljava"]
    #[desni, lijevi]
    susjed = [size-1, 1]
elif rank == size-1:
    drzi_vilice = [None, None]
    susjed = [size-2, 0]
else:
    drzi_vilice = [None, "prljava"]
    susjed = [rank-1, rank+1]

zahtjevi = [False, False] #zahtjevi koje mogu ispuniti tek kad pojedem jer su mi sada vilice ciste



    

def ispuni_zahtjeve_za_vilicom(LiliD, i): #desna=0, lijeva=1

    #ako ja imam tu vilicu onda mu ju moram dati (ali samo ako je prljava) -> ako ju nema on onda ju sigurno imam ja
    #čistim vilicu i šaljem mu ju
    if drzi_vilice[LiliD] == "cista":
        #spremiti zahtjev!!! i poslati tu vilicu kad postane prljava
        zahtjevi[LiliD]=True
        return
    elif drzi_vilice[LiliD] == "prljava":
        primljena_poruka = comm.irecv(source = susjed[i], tag = 10+LiliD+1) #prije je to bio tag 0
        primljena_poruka.wait()
        req = comm.isend("cista", dest=susjed[i], tag=20+LiliD+1)
        req.wait()
        drzi_vilice[LiliD] = None

    return

#primi poruku od lijevog ili desnog susjeda i daj mu vilicu ako ju imas
def ispuni_zahtjeve(i):
    global drzi_vilice

    if comm.iprobe(susjed[i], 11): #desna
        ispuni_zahtjeve_za_vilicom(0,i) #desna
    if comm.iprobe(susjed[i], 12): #lijeva
        ispuni_zahtjeve_za_vilicom(1,i) #lijeva

    return



    





def misli():
    print('\t'*(rank) +"mislim")
    sys.stdout.flush()

    for t in range(1,randint(1,5)+1):
        ispuni_zahtjeve(0)
        ispuni_zahtjeve(1)
        sleep(1)
    ispuni_zahtjeve(0)
    ispuni_zahtjeve(1)

    return

def nabavi_vilice():
    global drzi_vilice

    if len(drzi_vilice) - drzi_vilice.count(None) == 2:
        return

    #sve dok nemas 2 vilice trebas ih traziti -> 
    #       kad imas 1 cistu znas da ti treba jedino 1 nova i nitko ti ne moze uzeti trenutnu
    #       kad imas 1 prljavu netko ti ju moze uzet
    #       cim imas 2 vilice ti si spreman za dalje
    #pošalji zahtjev za vilicom koju nemaš i cekaj dok ju ne dobijes
    while len(drzi_vilice) - drzi_vilice.count(None) < 2:
        for i in range(0,2): #i=0, i=1
            if drzi_vilice[i] is None:               

                # #ako me netko trazi vilicu onda ne mogu pitat za njegovu vilicu nego ju mu moram dati
                # ispuni_zahtjeve(0)
                # ispuni_zahtjeve(1)
                if comm.iprobe(source = susjed[0]) or comm.iprobe(source = susjed[1]):
                    ispuni_zahtjeve(0)
                    ispuni_zahtjeve(1)


                print('\t'*(rank) + "trazim vilicu (" + str(susjed[i]) + ")") #i oznacaja desnu odnosno lijevu vilicu
                sys.stdout.flush()

                #pitam susjeda da mi da tu vilicu
                #npr ako mi treba desna vilica onda pitam desnog susjeda da mi da svoju lijevu vilicu
                if i==0:
                    j=1
                elif i==1:
                    j=0

                req = comm.isend("prljava", dest=susjed[i], tag=10+j+1)
                
                #cekaj poruku (bilo koju!);
                #ako je poruka odgovor na zahtjev azuriraj vilice; 
                #inace ako je poruka zahtjev obradi zahtjev (odobri ili zabiljezi);
                while True:
                    #tag = 1
                    if comm.iprobe(source = susjed[i], tag= 20+j+1):
                        primljena_poruka = comm.irecv(source = susjed[i], tag= 20+j+1)
                        primljena_poruka.wait()
                        drzi_vilice[i] = "cista"
                        break
                            
                    #tag = 0
                    #dal netko trazi vilicu, ali onu drugu jer vilicu i jos nemas
                    elif comm.iprobe(source = susjed[j], tag=10+j+1):
                        ispuni_zahtjeve(j)
    return

def jedi():
    global zahtjevi
    
    print('\t'*(rank) + "jedem")
    sys.stdout.flush()
    sleep(randint(1,5))
    drzi_vilice[0] = "prljava"
    drzi_vilice[1] = "prljava"


    #odgovori na zahtjeve koji cekaju
    if zahtjevi[0]:
        ispuni_zahtjeve(0)
    if zahtjevi[1]:
        ispuni_zahtjeve(1)

    #ove linije koda znace da on mora nakon jela odgovoriti na zahtjeve koje je dobio dok je jeo - mislim da se to ne trazi
    # if not zahtjevi[0]:
    #     ispuni_zahtjeve(0)
    # if not zahtjevi[1]:
    #     ispuni_zahtjeve(1)

    zahtjevi = [False, False]

    return


def Proces():
    misli()		        # ispis: mislim
    nabavi_vilice()     # ispis: trazim vilicu (indeks)
    jedi()		        # ispis: jedem


while True:
    Proces()