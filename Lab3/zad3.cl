__kernel void jacobi_step(__global float* psi, __global float* psinew, int m, int n, int psi_size, int broj_dretvi){

    __private uint gid = get_global_id(0);  //gid je id dretve
    __private uint i;
    __private uint j;
    __private uint c;

    for(c = gid; c < (m*n); c+=broj_dretvi) {

        if (c >= psi_size){
            break;
        }

        i = (c % m) + 1;
		j = ((c / m) % n) + 1;

        psinew[i * (m + 2) + j] = 0.25 * (psi[(i - 1) * (m + 2) + j] + psi[(i + 1) * (m + 2) + j] + psi[i * (m + 2) + j - 1] + psi[i * (m + 2) + j + 1]);
	
    }

}


__kernel void deltasq(__global float* newarr, __global float* oldarr, __global float* dsq,  int m, int n, int arr_size, int broj_dretvi){

    __private uint gid = get_global_id(0);  //gid je id dretve
    __private uint c;

    __private float tmp = 0.0;

    __private uint i;
    __private uint j;

    for(c = gid; c < (m*n); c+=broj_dretvi) {

        i = (c % m) + 1;
		j = ((c / m) % n) + 1;

        tmp = newarr[i*(m+2)+j]-oldarr[i*(m+2)+j];
        dsq[gid] += tmp*tmp;

    }

    barrier(CLK_LOCAL_MEM_FENCE);

    if (gid == 0) {

        __private float sum = 0.0;

        for(i = 0; i < broj_dretvi; i++) {
            sum += dsq[i];
        }

        dsq[0] = sum;

    }

}



__kernel void copyback(__global float* copy_from_here, __global float* copy_to_here, int m, int n, int arr_size, int broj_dretvi){

    __private uint gid = get_global_id(0);  //gid je id dretve
    __private uint c;

    __private uint i;
    __private uint j;

    for(c = gid; c < (m*n); c+=broj_dretvi) {

        i = (c % m) + 1;
		j = ((c / m) % n) + 1;

        copy_to_here[i*(m+2)+j]=copy_from_here[i*(m+2)+j];
        
    }

}


