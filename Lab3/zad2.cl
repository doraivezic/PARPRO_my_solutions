__kernel void prim( __global float* rezultat, int N, int broj_dretvi){

        __private uint gid = get_global_id(0);  //gid je id dretve
        __private uint i;
        __private uint j;

        //printf("broj %d %d\n",gid, broj_dretvi );

        
        for(i = gid+1; i <= N; i+=broj_dretvi) {

            __private float a = 0.0;

            a = ((float)i - 0.5) / N;
            rezultat[gid] += 1.0 / (1.0 + a*a); 
            
        }

        barrier(CLK_LOCAL_MEM_FENCE);

        if (gid == 0) {

            __private float sum = 0;

            for(i = 0; i < broj_dretvi; i++) {
                sum += rezultat[i];
            }

            sum = sum * 4.0/N;

            rezultat[0] = sum;

        }

    }