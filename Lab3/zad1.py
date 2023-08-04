import pyopencl as cl
import numpy as np
import random
import time

from zajednicka_klasa import Paralelno_izvodenje


#ODREĐIVANJE BROJ PRIM BROJEVA U ULAZNOM NIZU

if __name__ == "__main__":

    p = Paralelno_izvodenje("zad1.cl")

    N = 20     #broj elemenata niza (potencija broja 2)
    L = np.int32(64)    #veličine grupe dretvi (L)
    G = np.int32(L * 100)  #broj dretvi; globalne veličine skupa dretvi (G); 
    
    #ulazni_niz = np.array([5,2,25,78,1,0,100]).astype(np.int32)
    ulazni_niz = np.array(random.choices(range(1, 1000), k=2**N)).astype(np.int32)
    prim_brojevi = np.empty( 1, dtype=np.int32)



    #SLIJEDNO IZVOĐENJE

    # trajanje_poteza_start = time.time()

    # sum = 0
    # for num in ulazni_niz:
    #     prim_je = True
    #     if num > 1:
    #         for i in range(2, num):
    #             if (num % i) == 0:
    #                 prim_je = False
    #                 break
    #         if prim_je:
    #             sum += 1

    # trajanje_poteza_end = time.time()
    
    # print("Slijedno:", sum, " Trajanje:", trajanje_poteza_end - trajanje_poteza_start)



    #PARALELNO IZVOĐENJE

    trajanje_poteza_start = time.time()

    buffer_ulazni_niz = cl.Buffer(p.getContext(),   p.getFlags().READ_ONLY | p.getFlags().COPY_HOST_PTR, hostbuf=ulazni_niz)
    buffer_prim_brojevi = cl.Buffer(p.getContext(), p.getFlags().READ_WRITE , prim_brojevi.nbytes)
    
    p.getProgram().prim(p.getQueue(), (G,), (L,), buffer_ulazni_niz, buffer_prim_brojevi, np.int32(len(ulazni_niz)), G).wait()
    cl.enqueue_copy(p.getQueue(), prim_brojevi, buffer_prim_brojevi)

    trajanje_poteza_end = time.time()

    print("Paralelno:", prim_brojevi[0], " Trajanje:", trajanje_poteza_end - trajanje_poteza_start)


    exit(0)

