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
#include <sys/wait.h>



int NUMPROC = 1;
int MAXPROC = 5;
int procCount = 0;
pid_t child_pid, wpid;
int status = 0;
int i;

//int ***aggregates;

void proc_wait();

int main( int argc, char const *argv[] ) {    

    if (argc == 4) {
					
		char const *param = argv[1];
		char const *inputDirectory = argv[2];
		char const *outputDirectory = argv[3];
		int nrFiles = 12;
		printf("Using %s\n", param);

		//read paramater file
    	if (mcInit(param) == -1) {
    		return(0);
    	}

	    //start processes
	    printf("parent_pid = %d\n", getpid());
	    for (i = 0; i < NUMPROC; i++)
	    {
	        //start process
	        procCount++;
	        if ((child_pid = fork()) == 0) {
	        	
	        		/* run dispersal model */
					mcMigrate(&param, &nrFiles, inputDirectory, outputDirectory);

					return(0);				
	        }

	        /* wait for child processes to return if over process limit */
	        proc_wait();	        
	    }

	    /* Wait for remaining processes to finish */
	    while ((wpid = wait(&status)) > 0)
	    {
	        printf("Exit status of %d was %d (%s)\n", (int)wpid, status,
	               (status > 0) ? "failed" : "success");
	    }

	/* Bad command line arguments */
    } else {
				
		printf("\n\nInvalid arguments. \nExpected:\nmig [parameter file location] [input location] [output location]\n\n");
		return(-1);		
	}

	return(1);
}

/*void setupAggregates() {
	int i,j,k;
	// Allocate memory for the aggregates and zero
    printf("Dispersal Steps: %d\nNrRows: %d\nNrCols: %d\n", dispSteps, nrRows, nrCols);
    aggregates = (int ***)malloc (dispSteps * sizeof (int **));
    for (i=0; i<dispSteps;i++) {
        aggregates[i] = (int **)malloc (nrRows * sizeof (int *));
        for (j=0;j<nrRows;j++) {
            aggregates[i][j] = (int *)malloc (nrCols * sizeof (int));
            for (k=0;k<nrCols;k++) {
                aggregates[i][j][k] = 0;
            }
        }
    }
}*/


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