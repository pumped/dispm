#include "migclim.h"
#include "migrate.c"
#include "file_io.c"
#include "genclust.c"
#include "barriers.c"
#include "univ_disp.c"
#include "src_cell.c"

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>

#include <semaphore.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/shm.h>



int NUMPROC = 3;
int MAXPROC = 3;
int procCount = 0;
pid_t child_pid, wpid;
int status = 0;
int i;

char const *outputDirectory;
bool *written;
bool quit = false;



int main( int argc, char const *argv[] ) {    

    if (argc == 4) {
					
		char const *param = argv[1];
		char const *inputDirectory = argv[2];
		outputDirectory = argv[3];
		int nrFiles = 12;

		//read paramater file
    	if (mcInit(param) == -1) {
    		return(0);
    	}

    	printf("Allocating Memory \n");

    	//setup aggregates shared memory
		shmid2 = shmget(IPC_PRIVATE, nrRows*nrCols*dispSteps * sizeof aggregates_data[0], IPC_CREAT | 0700);
		aggregates_data = shmat(shmid2, NULL, 0); //attach for parent
		shmctl (shmid2 , IPC_RMID , 0);

		//setup write tracker
		setupStepCompleteArray();


		indexAggregates();
		zeroAggregates();
		printf("Zeroed \n");

	    //start processes
	    for (i = 0; i < NUMPROC+1; i++)
	    {
	        //start process
	        procCount++;
	        if ((child_pid = fork()) == 0) { // child process
	        		procID = i;
	        		if (i == 0) {
	        			writeThread();
	        			return(0);
	        		}

	        		//attach aggregates
	        		aggregates_data = shmat(shmid2, NULL, 0);
	        		indexAggregates();
	        		/* run dispersal model */
					mcMigrate(&param, &nrFiles, inputDirectory, outputDirectory);
					deIndexAggregates();
					return(0);				
	        }

	        /* wait for child processes to return if over process limit */
	        proc_wait();
	        sleep(1);        
	    }

	    /* Wait for remaining processes to finish */
	    while ((wpid = wait(&status)) > 0)
	    {
	        if (status != 0) {
	        	printf("Exit status of %d was %d (%s)\n", (int)wpid, status,
	            	   (status > 0) ? "failed" : "success");
	    	}	
	    }

	    cleanupStepCompleteArray();

	    /* write out aggregates */	    
	    /*for (i=0; i<dispSteps;i++) {
	    	writeAggregateFile(i, outputDirectory);
		}*/
	    quit = true;

		//cleanup
	    deIndexAggregates();
	    
	    

	/* Bad command line arguments */
    } else {
				
		printf("\n\nInvalid arguments. \nExpected:\nmig [parameter file location] [input location] [output location]\n\n");
		return(-1);		
	}

	return(1);
}

void writeThread() {
	int m;
	
	printf("Write Thread Running\n");

	written = malloc(dispSteps*sizeof(bool));
	for (m=0; m < dispSteps; m++) {
		written[m] = false;
	}

	//wait for array
	//bool quit = false;
	bool allWritten;

	while (!quit) {
		allWritten = true;
		for (m = 0; m < dispSteps; m++) {
			if (stepComplete[m] >= NUMPROC-1 && !written[m]) {
				written[m] = true;

				// write it
				writeAggregateFile(m,outputDirectory);
				//printf("Writing: %d\n",m);
			}
			if (!written[m]) {
				allWritten = false;
			}
		}

		if (allWritten) {
			quit = true;
		}

		//printf("Waiting\n");
		sleep(1);
		//printf("Awake\n");
	}

	printf("Writing Finished");

	//write aggregate
}

void writeAggregateFile(int i, char const *outputDirectory) {
	char    fileName[128];
	char	fileLCKName[128];
	double time_spent;
	clock_t start = clock();
	
	//setup data headers
	nrCols = 3084;
	nrRows = 5045;
	xllCorner = 143.916567517;
	yllCorner = -20.02510726;
	cellSize = 0.001;
	noData = -9999;
    

    sprintf(fileName, "%s/agg%i.asc", outputDirectory,i);
    sprintf(fileLCKName, "%s.LCK",fileName);
    
    //write lock
    writeLock(fileLCKName);

    //write matrix
    writeMat(fileName, aggregates[i]);
    
    //remove lock
    deleteLock(fileLCKName);

    time_spent = (double)(clock() - start) / CLOCKS_PER_SEC;
    printf("Write %i : %lf \n",i,time_spent);
}

void writeLock(char const *lockPath) {
	FILE *fp;
	if ((fp = fopen(lockPath,"w")) == NULL) {
		printf("can't open lock file");
	}
	fprintf(fp,"l");
	fclose(fp);
}

void deleteLock(char const *lockPath) {
	if (unlink(lockPath) == -1) {
		printf("failed to delete lock %s\n",lockPath);
	}
}

void setupStepCompleteArray() {
	//create semaphore and shared memory
    stepComplete_shmkey = ftok ("/dev/null", 5);
    stepComplete_shmid = shmget (stepComplete_shmkey, dispSteps*sizeof (int), 0644 | IPC_CREAT);
    if (stepComplete_shmid < 0){  perror ("shmget\n"); exit (1); } //exit on error
    //shmctl (stepComplete_shmid , IPC_RMID , 0);
    stepComplete = (int *) shmat (stepComplete_shmid, 0, 0);   /* attach p to shared memory */

    //open sem and set auto unlink
    stepCompleteLock = sem_open ("pSem", O_CREAT | O_EXCL, 0644, 1); 
    sem_unlink ("pSem"); 
}

void cleanupStepCompleteArray() {
		/* shared memory detach */
        shmdt ((void *) stepComplete);
        shmctl (stepComplete_shmid, IPC_RMID, 0);

        /* cleanup semaphores */
        sem_destroy (stepCompleteLock);
}

void incrementStepComplete(int i) {
	sem_wait(stepCompleteLock);
    stepComplete[i] += 1;
    //printf ("Step Incremented: p[%d] = %d \n",i,stepComplete[i]);
    sem_post(stepCompleteLock);
}

void indexAggregates() {
	/* Index Aggregates for easier access */
	int i,j,k;
    aggregates = (int***)malloc(dispSteps * sizeof(int**));
	for (i=0; i < dispSteps; i++) {
		aggregates[i] = (int**)malloc(nrRows * sizeof(int*));
		for (j=0; j < nrRows; j++) {
			aggregates[i][j] =  (int*)(aggregates_data + (i * nrRows * nrCols) + (j * nrCols));
		}
	}
}

void zeroAggregates() {
	int i,j,k;
	for (i=0; i < dispSteps; i++) {
		for (j=0; j < nrRows; j++) {
			for (k=0; k < nrCols; k++) {
				aggregates[i][j][k] = 0;
			}
		}
	}
}

void deIndexAggregates() {
	int i,j;
	if (aggregates != NULL) {
        for (i = 0; i < dispSteps; i++) {
            free(aggregates[i]);
        }
        free(aggregates);
    }
}

void proc_wait() {
    /* If at process limit, wait for other processes to finish */
    if (procCount >= MAXPROC) {
        printf("waiting\n");
        if ((wpid = wait(&status)) > 0)
        {
            procCount--;
            printf("Exit status of %d was %d (%s)\n", (int)wpid, status,
                   (status > 0) ? "accept" : "reject");
        }
    }
}
