#include <pthread.h>
#include <stdio.h>

#define ARRAYSIZE 1700
#define NUMTHREADS 6

struct ThreadData {
	int start, stop;
	int* array;
};

/* puts i^2 into array positions i=start to stop-1 */
void* squarer(struct ThreadData* td) {
    struct ThreadData* data=(struct ThreadData*) td;
    int start=data->start;
    int stop=data->stop;
    int* array=data->array;
    int i;

    printf ("Thread Running \n");

    for (i=start; i<stop; i++) {
        array[i]=i*i;
    }

    return NULL;
}

int main(void) {
    int array[ARRAYSIZE];
    pthread_t thread[NUMTHREADS];
    struct ThreadData data[NUMTHREADS];
    int i;
    /*
        this has the effect of rounding up the number of tasks
        per thread, which is useful in case ARRAYSIZE does not
        divide evenly by NUMTHREADS.
    */
    int tasksPerThread=(ARRAYSIZE+NUMTHREADS-1)/NUMTHREADS;

    /* Divide work for threads, prepare parameters */
    for (i=0; i<NUMTHREADS; i++) {
        data[i].start=i*tasksPerThread;
        data[i].stop=(i+1)*tasksPerThread;
        data[i].array=array;
    }
    /* the last thread must not go past the end of the array */
    data[NUMTHREADS-1].stop=ARRAYSIZE;

    /* Launch Threads */
    for (i=0; i<NUMTHREADS; i++) {
        pthread_create(&thread[i], NULL, squarer, &data[i]);
    }

    /* Wait for Threads to Finish */
    for (i=0; i<NUMTHREADS; i++) {
        pthread_join(thread[i], NULL);
        printf("Thread Terminated \n");
    }

    /* Display Result */
    /*for (i=0; i<ARRAYSIZE; i++) {
        printf("%d ", array[i]);
    }*/
    //printf("\n");

    return 0;
}