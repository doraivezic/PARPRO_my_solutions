import pyopencl as cl
import numpy as np
import time

from zajednicka_klasa import Paralelno_izvodenje


#CFD

if __name__ == "__main__":

    cfd = Paralelno_izvodenje("zad3.cl")


    G = np.int32(64 * 5)

    error, bnorm, tolerance, scalefactor, numiter, printfreq = 0.0, 0, 0, 0, 0, 1000
    bbase, hbase, wbase, mbase, nbase = 10, 15, 5, 32, 32 #5, 5, 3, 8, 8
    irrotational, checkerr = 1, 0
    m, n, b, h, w, iter, i, j = 0, 0, 0, 0, 0, 0, 0, 0
    tstart, tstop, ttot, titer = 0, 0, 0, 0

    scalefactor, numiter = 64, 1000

    b = bbase*scalefactor
    h = hbase*scalefactor
    w = wbase*scalefactor
    m = mbase*scalefactor
    n = nbase*scalefactor

    psi = np.zeros(((m+2)*(n+2)), dtype=np.float32)
    psinew = np.zeros(((m+2)*(n+2)), dtype=np.float32)
    i, j = 0, 0



    for i in range(b+1, b+w):
        psi[i*(m+2)+0] = i-b
        
    for i in range(b+w, m+1):
        psi[i*(m+2)+0] = w

    for j in range(1, h+1):
        psi[(m+1)*(m+2)+j] = w

    for j in range(h+1, h+w):
        psi[(m+1)*(m+2)+j]= w-j+h


    bnorm=0.0
    for i in range(0, m+2):
        for j in range(0, n+2):
            bnorm += psi[i*(m+2)+j]*psi[i*(m+2)+j]
    bnorm = np.sqrt(bnorm)

    
    
    #PARALELNO IZVOĐENJE - samo za irrotational

    print("\nStarting main loop...\n")

    trajanje_poteza_start = time.time()

    for iter in range(1, numiter+1):

        #jacobi_step
        buffer_psi = cl.Buffer(cfd.getContext(),   cfd.getFlags().READ_ONLY | cfd.getFlags().COPY_HOST_PTR, hostbuf=psi)
        buffer_psinew = cl.Buffer(cfd.getContext(), cfd.getFlags().READ_WRITE | cfd.getFlags().COPY_HOST_PTR, hostbuf=psinew)
        
        cfd.getProgram().jacobi_step(cfd.getQueue(), (G,), None, buffer_psi, buffer_psinew, np.int32(m), np.int32(n), np.int32((m+2)*(n+2)), G).wait()
        cl.enqueue_copy(cfd.getQueue(), psinew, buffer_psinew)

    
        if checkerr or iter == numiter: 
            dsq = 0

            #deltasq
            buffer_psi = cl.Buffer(cfd.getContext(),   cfd.getFlags().READ_ONLY | cfd.getFlags().COPY_HOST_PTR, hostbuf=psi)
            buffer_psinew = cl.Buffer(cfd.getContext(), cfd.getFlags().READ_ONLY | cfd.getFlags().COPY_HOST_PTR, hostbuf=psinew)
            dsq_list = np.empty( G, dtype=np.float32)
            buffer_dsq = cl.Buffer(cfd.getContext(), cfd.getFlags().READ_WRITE, dsq_list.nbytes)
            
            cfd.getProgram().deltasq(cfd.getQueue(), (G,), None, buffer_psinew, buffer_psi, buffer_dsq, np.int32(m), np.int32(n), np.int32((m+2)*(n+2)), G).wait()
            cl.enqueue_copy(cfd.getQueue(), dsq_list, buffer_dsq)

            dsq = dsq_list[0]

            error = dsq
            error=np.sqrt(error)
            error=error/bnorm

        if checkerr: 
            if (error < tolerance):
                print("Converged on iteration", iter)
                break

        #copy back psinew u psi
        buffer_psi = cl.Buffer(cfd.getContext(),   cfd.getFlags().READ_WRITE | cfd.getFlags().COPY_HOST_PTR, hostbuf=psi)
        buffer_psinew = cl.Buffer(cfd.getContext(), cfd.getFlags().READ_ONLY | cfd.getFlags().COPY_HOST_PTR, hostbuf=psinew)
        
        cfd.getProgram().copyback(cfd.getQueue(), (G,), None, buffer_psinew, buffer_psi, np.int32(m), np.int32(n), np.int32((m+2)*(n+2)), G).wait()
        cl.enqueue_copy(cfd.getQueue(), psi, buffer_psi)

        

        if(iter%printfreq == 0):
            if not checkerr:
                print("Completed iteration", iter)
            else:
                print("Completed iteration", iter, "error =", error)

    if iter > numiter:
        iter=numiter

    trajanje_poteza_end = time.time()
    
    print("\n... finished\n")
    t = trajanje_poteza_end - trajanje_poteza_start
    print("Paralelno izvođenje, konačna greška:", error, " \nUkupno trajanje:", t, "\nTrajanje svake iteracije:", t/iter)


    exit(0)

