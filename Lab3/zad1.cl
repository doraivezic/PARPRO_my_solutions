__kernel void prim(__global int* ulazni, __global int* rezultat, int duljina, int N){

        __private uint gid = get_global_id(0);  //gid je id dretve
        // __private uint lid = get_local_id(0);
        // __private uint dim = get_work_dim();
        // printf("(%d)(%d)(%d)\t", gid, lid, dim);

        __private uint broj_dretvi = N;
        __private uint i;
        __private uint j;

        volatile __global int* counterPtr = &rezultat[0]; 

        
        for(i = gid; i < duljina; i+=broj_dretvi) {

            __private uint num = ulazni[i];

            __private uint var = 0;

            if (num > 1){

                for( j=2; j<num; j+=1 ){
                    if ((num % j) == 0){
                        var = 1;
                        break;
                    }
                }
                
                if (var == 0){  //num je prim
                    //rezultat[0] += 1;   
                    atomic_inc(counterPtr);
                }

            } //ako je broj 1 ili manji onda nije prim

        }

    }