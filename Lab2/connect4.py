#polje 6visine x 7širina - bez pretpostavke o neograničenosti polja u visinu
#oblik stabla - zadana dubina
#za svaki potez računala se odabire sljedece stanje - uvijek se radi pretraga podstabla

#pobjeda - računalo ima 4 u nizu (+1)
#poraz - igrač ima 4 u nizu (-1)
#neutralno stanje (0)

#minimalna dubina: n=4
#minimalan broj poteza: 7


#mpiexec -n 2 python connect4.py  #broj procesa se tu odabire

from math import log2
from mpi4py import MPI
import mpi4py
from random import randint
import sys
import time

mpi4py.rc.recv_mprobe = False
mpi4py.rc.threads = False

from polje import Polje

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

#definiranje polja
VISINA_POLJA = 6
SIRINA_POLJA = 7
DUBINA_STABLA = 7

#pricekaj sve procese
comm.Barrier()


def evaluate(polje, zadnji_igrao, stupac, dubina): #trenutno polje, poslijednje odigravanje, dubina stable
    
    #provjeri kraj igre
    #provjeri jesam li pobijedio
    kraj = polje.provjeri_kraj(stupac)
    if kraj:
        if zadnji_igrao == Polje.COMP:
            return 1
        else:
            return -1
    
    #igra nije gotova - dolje idemo u iducu razinu - ovdje provjeravamo je li gotovo
    if dubina==0:
        return 0
    
    #provjeri tko je napravio zadnji potez, a tko je sad na potezu
    if zadnji_igrao == Polje.COMP:
        sada_igra = Polje.USER
    else:
        sada_igra = Polje.COMP

    #ocjena
    suma = 0.0
    potezi = 0.0 #broj mogucih poteza u toj razini
    sve_pobjeda = True; sve_poraz = True
    for i in range(SIRINA_POLJA):  #stupac je i+1
        if polje.provjeri_unos(i+1):
            potezi += 1
            polje.odigraj(sada_igra, i+1)
            rez = float(evaluate(polje, sada_igra, i+1, dubina-1))
            polje.ukloni_odigravanje(i+1)

            if rez > -1: sve_poraz = False  #sva djeca nisu porazi
            if rez != 1: sve_pobjeda = False 
            if rez == 1 and sada_igra == Polje.COMP: return 1    #svojim potezom mogu doci do pobjede (pravilo 1)
            if rez == -1 and sada_igra == Polje.USER: return -1  #protivnik moze potezom doci do pobjede (pravilo 2)

            suma += rez

    #pravilo 3
    if sve_pobjeda: return 1
    if sve_poraz: return -1

    if potezi>0:
        return suma/potezi  # ocjena / broj mogucih poteza iz zadanog stanja
    else:
        return -1


def ugasi_sve_procese():
    for worker in range(1,size):
        comm.send(200, dest=worker)
    exit(0)
    return


def potez_user(igra):
    #korisnik je na redu
    while True:
        izabrani_stupac = input("Unesi stupac (1-7) ili 0 za kraj: ")
        try:
            izabrani_stupac = int(izabrani_stupac)
            if not (izabrani_stupac>=0 and izabrani_stupac<=SIRINA_POLJA):
                raise ValueError()
            #provjeri unos: je li taj stupac slobodan?
            elif not igra.provjeri_unos(izabrani_stupac):
                print("Taj stupac je pun!")
                raise ValueError()
            else:
                break
        except:
            print("Neispravan unos !")
    
    if izabrani_stupac == 0:
        print("Korisnik je odustao. Pobijedilo je racunalo!")
        ugasi_sve_procese()
    
    igra.odigraj(Polje.USER, izabrani_stupac)
    igra.print_polje()

    unosi.append(izabrani_stupac)

    #provjeri je li korisnik pobijedio
    kraj = igra.provjeri_kraj(izabrani_stupac)
    if kraj:
        print("Pobijedio je korisnik!")
        ugasi_sve_procese()

    #provjeri ima li mjesta na ploci za jos igre
    if not igra.provjeri_mjesta():
        print("Nitko nije pobijedio. Rezultat je nerjesen!")
        ugasi_sve_procese()

    return igra




#master - drži polje
if rank == 0: 

    igra = Polje(SIRINA_POLJA, VISINA_POLJA)
    unosi = []


    if size == 1:

        while True:
            trajanje_poteza_start = time.time()

            #COMP na redu

            for stupac in range(1, SIRINA_POLJA+1):
                kraj = igra.provjeri_kraj(stupac)
                if kraj:
                    print("Igra završena!")
                    ugasi_sve_procese()

            dubina = DUBINA_STABLA -1
            najbolji_rez = -1
            najbolji_stupac = -1
            #treba nam petlja jer ako svi potezi vode u poraz onda racunamo opet za duplo manju dubinu
            while najbolji_rez==-1 and dubina>0:

                najbolji_rez = -1
                najbolji_stupac = -1
                for column in range(1, SIRINA_POLJA+1):
                    if igra.provjeri_unos(column):

                        if najbolji_stupac==-1: najbolji_stupac=column

                        igra.odigraj( Polje.COMP, column )
                        rez = evaluate(igra, Polje.COMP, column, dubina) 
                        igra.ukloni_odigravanje(column)

                        if najbolji_rez < rez or (rez == najbolji_rez and randint(1,2)%2==0):
                            najbolji_rez = rez
                            najbolji_stupac = column

                dubina = dubina / 2

            trajanje_poteza_end = time.time()
            print("Trajanje poteza: ", trajanje_poteza_end - trajanje_poteza_start, "s")

            #odigraj potez
            igra.odigraj(Polje.COMP, najbolji_stupac)
            igra.print_polje()


            igra = potez_user(igra)


    


    #dok igra traje (ja sam prvi na potezu)
    while True:

        trajanje_poteza_start = time.time()


        #pronađi potez koji zelis odigrat, ali prvo podijeli zadatke

        broj_zadataka = SIRINA_POLJA ** int(log2(size-1))

        #napraviti zadatke i poslati proceesima
        zadaci = []
        for i in range(broj_zadataka):
            zadaci.append(None)
            
        #pokreni komunikaciju sa radnicima - oni ce rec kad su gotovi sa svojim zadatkom i uzet ce novi
        for worker in range(1, size-1 +1):
            #obzirom da ne radi neblokirajuca komunikacija, nego se pickle ne moze ispravno citati, potrebno je korsititi blokirajucu
            comm.send(unosi, tag=worker-1, dest = worker)
            zadaci[worker-1] = -2

        ###ZADACI IMAJU VRIJEDNOSTI: None (ako ga jos nismo pokrenuli), -2 (ako se izvrsava), vrijednost (-1,1,ostalo)

        #kad je radnik slobodan on zeli novi zadatak
        while (None in zadaci) or (-2 in zadaci):
            status = MPI.Status()
            msg = comm.Probe(source=MPI.ANY_SOURCE,status=status)
            message = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            zadaci[status.Get_tag()] = message
            worker = status.Get_source()

            if None in zadaci:
                zadatak = zadaci.index(None)
                comm.send(unosi, tag=zadatak, dest = worker)
                zadaci[zadatak] = -2
            

        #izracunaj kvalitetu poteza uz pomocu svih izvrsenih zadataka i uzmi najboji stupac
        kvaliteta_svih_poteza = []
        #(broj_pobjeda_u_dubini_n - broj_poraza_u_dubini_n)/(broj_mogućih_poteza)
        #od svih zadataka gledaj ono prvo grananje - razina sa 7 cvorova
        for i in range(SIRINA_POLJA):
            suma = 0
            for j in range( int(len(zadaci)*(i/SIRINA_POLJA)), int(len(zadaci)* (i+1)/SIRINA_POLJA) ):
                suma += zadaci[j]
            kvaliteta_svih_poteza.append(suma/SIRINA_POLJA)

        #print(kvaliteta_svih_poteza)
        
        izabrani_stupac = kvaliteta_svih_poteza.index(max(kvaliteta_svih_poteza))+1

        trajanje_poteza_end = time.time()
        print("Trajanje poteza: ", trajanje_poteza_end - trajanje_poteza_start, "s")


        #odigraj potez
        igra.odigraj(Polje.COMP, izabrani_stupac)
        igra.print_polje()

        unosi.append(izabrani_stupac)

        #provjeri jesam li pobijedio
        kraj = igra.provjeri_kraj(izabrani_stupac)
        if kraj:
            print("Pobijedilo je racunalo!")
            ugasi_sve_procese()

        #provjeri ima li mjesta na ploci za jos igre
        if not igra.provjeri_mjesta():
            print("Nitko nije pobijedio. Rezultat je nerjesen!")
            ugasi_sve_procese()

        #korisnik je na redu
        while True:
            izabrani_stupac = input("Unesi stupac (1-7) ili 0 za kraj: ")
            try:
                izabrani_stupac = int(izabrani_stupac)
                if not (izabrani_stupac>=0 and izabrani_stupac<=SIRINA_POLJA):
                    raise ValueError()
                #provjeri unos: je li taj stupac slobodan?
                elif not igra.provjeri_unos(izabrani_stupac):
                    print("Taj stupac je pun!")
                    raise ValueError()
                else:
                    break
            except:
                print("Neispravan unos !")
                
        if izabrani_stupac == 0:
                print("Korisnik je odustao. Pobijedilo je racunalo!")
                ugasi_sve_procese()

        igra.odigraj(Polje.USER, izabrani_stupac)
        igra.print_polje()

        unosi.append(izabrani_stupac)

        #provjeri je li korisnik pobijedio
        kraj = igra.provjeri_kraj(izabrani_stupac)
        if kraj:
            print("Pobijedio je korisnik!")
            ugasi_sve_procese()

        #provjeri ima li mjesta na ploci za jos igre
        if not igra.provjeri_mjesta():
            print("Nitko nije pobijedio. Rezultat je nerjesen!")
            ugasi_sve_procese()


#worker
else:

    igraci = [Polje.COMP, Polje.USER]
    while True:

        status = MPI.Status()
        unosi = False
        unosi = comm.recv(source=0, status=status)

        if type(unosi) == int:
            exit(0)

        tag = status.Get_tag() +1

        polje = Polje(SIRINA_POLJA, VISINA_POLJA)
        for i in range(len(unosi)):
            polje.odigraj(igraci[i%2], int(unosi[i]))
        
        #tag je index zadatka (od 0 do broj_zadataka-1)
        #zelim pronaci koje stupce i kojim redom moram uzet
        #npr za 7*49 zadataka, tag 45 : 45//7=6 (stupac 7), 45%7=3 (stupac 3) -> racunalo obavlja potez 7, korisnik obavlja potez 3

        #koliko razina tj poteza moram proc
        br_poteza = int(log2(size-1))

        niz_unosa_za_provjeru = []

        unos = tag % SIRINA_POLJA
        if unos==0:
            unos = SIRINA_POLJA
        niz_unosa_za_provjeru.append(unos)
        for i in range(1,br_poteza):
            unos = ((tag-1)// (SIRINA_POLJA**i)) % SIRINA_POLJA +1
            
            niz_unosa_za_provjeru.append(unos)

        niz_unosa_za_provjeru.reverse()

        zadnji_igrao = Polje.COMP
        odigrani = []
        pobjeda = 0
        #odigraj 1 po 1 potez i ako on vodi do necije pobjede, javi to masteru
        for i in range(len(niz_unosa_za_provjeru)):

            if polje.polje[VISINA_POLJA-1][niz_unosa_za_provjeru[i]-1] == '-':  #pazimo na granice polja
                polje.odigraj( igraci[i%2], niz_unosa_za_provjeru[i] )
                odigrani.append(niz_unosa_za_provjeru[i])
                zadnji_igrao = igraci[i%2]
            else:
                for j in range(len(odigrani)):
                    polje.ukloni_odigravanje(odigrani[j])  #ukloni samo one poteze koje smo obavili
                # print("saljem -1")
                # sys.stdout.flush()
                comm.send(-1, dest=0, tag=tag-1)
                pobjeda = -1
                break
    
            if polje.provjeri_kraj(niz_unosa_za_provjeru[i]):
                #polje.print_polje()
                # print(niz_unosa_za_provjeru)
                # sys.stdout.flush()
                for j in range(len(odigrani)):
                    polje.ukloni_odigravanje(odigrani[j])
                rez = 1  #pobjeda
                if j%2==1:
                    rez = -1  #poraz
                # print("saljem", rez)
                # sys.stdout.flush()
                comm.send(rez, dest=0, tag=tag-1)
                pobjeda = rez
                break


        if pobjeda!=0:
            continue

        #polje.print_polje()

        dubina = DUBINA_STABLA - (int(log2(size-1)) +1)
        najbolji_rez = -1
        najbolji_stupac = -1
        #treba nam petlja jer ako svi potezi vode u poraz onda racunamo opet za duplo manju dubinu
        while najbolji_rez==-1 and dubina>0:

            najbolji_rez = -1
            najbolji_stupac = -1
            for column in range(1, SIRINA_POLJA+1):
                if polje.provjeri_unos(column):

                    if najbolji_stupac==-1: najbolji_stupac=column

                    #neka sad igra onaj koji nije zadnji igrao
                    if zadnji_igrao == Polje.COMP:
                        zadnji_igrao = Polje.USER
                    else:
                        zadnji_igrao = Polje.COMP
                    polje.odigraj( zadnji_igrao, column )
                    rez = evaluate(polje, zadnji_igrao, column, dubina) 
                    polje.ukloni_odigravanje(column)

                    if najbolji_rez < rez or (rez == najbolji_rez and randint(1,2)%2==0):
                        najbolji_rez = rez
                        najbolji_stupac = column

            dubina = dubina / 2


        for j in range(len(odigrani)):
            polje.ukloni_odigravanje(odigrani[j])
                
        comm.send(najbolji_rez, dest=0, tag=tag-1)
        

        




        


        