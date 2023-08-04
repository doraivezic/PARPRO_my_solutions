import pyopencl as cl
import numpy as np
import random
import time

from zajednicka_klasa import Paralelno_izvodenje


#ODREĐIVANJE PI BROJA

if __name__ == "__main__":

    p = Paralelno_izvodenje("zad2.cl")

    G = np.int32(8)
    N = 1000000

    pi = np.empty( G, dtype=np.float32)



    #SLIJEDNO IZVOĐENJE - PI

    trajanje_poteza_start = time.time()

    sum = 0.0
    for i in range(1,N+1):
        a = (i-0.5)/N
        sum += 1 / (1 + a**2)
    sum = sum * 4.0/N

    trajanje_poteza_end = time.time()
    
    print("Slijedno: ", sum, " Trajanje:", trajanje_poteza_end - trajanje_poteza_start)



    #PARALELNO IZVOĐENJE

    trajanje_poteza_start = time.time()

    buffer_pi = cl.Buffer(p.getContext(), p.getFlags().READ_WRITE, pi.nbytes)
    
    p.getProgram().prim(p.getQueue(), (G,), None, buffer_pi, np.int32(N), G).wait()
    cl.enqueue_copy(p.getQueue(), pi, buffer_pi)

    trajanje_poteza_end = time.time()

    print("Paralelno: ", pi[0], " Trajanje:", trajanje_poteza_end - trajanje_poteza_start)


    exit(0)

