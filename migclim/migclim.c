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




int procCount = 0;
pid_t child_pid, wpid;
int status = 0;
int i;
int numActions = 6;

char const *outputDirectory;
bool quit = false;



int main( int argc, char const *argv[] ) {
  NUMPROC = 3;
  MAXPROC = 3;

    if (argc == 4) {

		char const *param = argv[1];
		char const *inputDirectory = argv[2];
		outputDirectory = argv[3];
		int nrFiles = 12;

		//read paramater file
    	if (mcInit(param) == -1) {
    		return(0);
    	}

      GDALAllRegister();

    	printf("Allocating Memory \n");

    //setup aggregates shared memory
		shmid2 = shmget(IPC_PRIVATE, nrRows*nrCols*dispSteps * sizeof aggregates_data[0], IPC_CREAT | 0700);
		aggregates_data = shmat(shmid2, NULL, 0); //attach for parent
		shmctl (shmid2 , IPC_RMID , 0);

		//setup write tracker
		setupStepCompleteArray();

    //setup management Actions
    readManagementActions(inputDirectory);
    //setup output array
    setupManagementArray();
    printf("Setup Management Array\n");
    indexManagementArray();
    zeroManagementArray();
    printf("Zeroed Management Array\n");

		indexAggregates();
		zeroAggregates();
		printf("Zeroed \n");

	    //start processes
	    for (i = 0; i < NUMPROC + 1; i++)
	    {
	        //start process
	        procCount++;
	        if ((child_pid = fork()) == 0) { // child process
	        		procID = i;
	        		if (i == 0) {
                if (fullOutput) {
                  writeThread();
                }
	        			return(0);
	        		}

	        		//attach aggregates
	        		aggregates_data = shmat(shmid2, NULL, 0);
	        		indexAggregates();

              //attach management outcomes
              managementImpacts_data = shmat(shmMAID, NULL, 0); //attach for parent
              indexManagementArray();


	        		/* run dispersal model */
					mcMigrate(&param, &nrFiles, inputDirectory, outputDirectory);

					/*if (procID == 1) {
	        			writeThread();
	        		}*/

	        		deIndexAggregates();

					return(0);
	        }

	        /* wait for child processes to return if over process limit */
	        proc_wait();
	        //usleep(100);
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

	printf("Write Thread Running (proc %d)\n",procID);

	/*written = malloc(dispSteps*sizeof(bool));
	*/

	//wait for array
	//bool quit = false;
	bool allWritten;

	while (!quit) {
		allWritten = true;

		for (m = 0; m < dispSteps; m++) {
			sem_wait(writeSynchroniser);
			//printf("checking");
			//printf("m %d",stepComplete[m]);
			if (stepComplete[m] >= NUMPROC && !written[m]) {
				written[m] = true;
				sem_post(writeSynchroniser);

				//printf("\nproc %i writing %d\n",procID,m);

				// write it
				writeAggregateFile(m,outputDirectory);
				//printf("Writing: %d\n",m);
			} else {
				sem_post(writeSynchroniser);
			}

			if (!written[m]) {
				//printf("not written");
				allWritten = false;
			}
		}

		if (allWritten) {
      printf("modelComplete : {\"finished\":1}");
			quit = true;
		}

		//printf("Waiting\n");
		usleep(50);
		//printf("Awake\n");
	}

	printf("Writing Finished (proc%d)\n",procID);

	//write aggregate
}

void writeAggregateFile(int matID, char const *outputDirectory) {
	char    fileName[128];
	//char	fileLCKName[128];
	double time_spent;
	clock_t start = clock();

	//setup data headers
	nrCols = 3084;
	nrRows = 5045;
	xllCorner = 143.916567517;
	yllCorner = -20.02510726;
	cellSize = 0.001;
	noData = -9999;

  sprintf(fileName, "%s/agg%i.tif", outputDirectory,matID+1);
  //sprintf(fileLCKName, "%s.LCK",fileName);

  //write lock
  //writeLock(fileLCKName);

  //write matrix
  writeMat(fileName, aggregates[matID]);

  //remove lock
  //deleteLock(fileLCKName);

  //sum
  int val = 0; // sum(matID);

  time_spent = (double)(clock() - start) / CLOCKS_PER_SEC;
  printf("Write %i : {\"time\":%lf,\"occupied\":%i}\n",matID+1,time_spent,val);
}

int sum(int matID) {
  int count = 0;
  //int occupationThreshold = NUMPROC / 2;
  int j,k;

  for (j=0; j < nrRows; j++) {
    for (k=0; k < nrCols; k++) {
      if (aggregates[matID][j][k] > 0) {
        count+= aggregates[matID][j][k];
      }
    }
  }

  return count / NUMPROC;
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
  stepComplete = (int *) shmat (stepComplete_shmid, 0, 0);   /* attach p to shared memory */
  shmctl (stepComplete_shmid , IPC_RMID , 0);

  //open sem and set auto unlink
  stepCompleteLock = sem_open ("pSem", O_CREAT | O_EXCL, 0644, 1);
  sem_unlink ("pSem");

  //create semaphore and shared memory
  written_shmkey = ftok ("/dev/null", 6);
  written_shmid = shmget (written_shmkey, dispSteps*sizeof (int), 0644 | IPC_CREAT);
  if (written_shmid < 0){  perror ("shmget\n"); exit (1); } //exit on error
  written = (int *) shmat (written_shmid, 0, 0);
  shmctl (stepComplete_shmid , IPC_RMID , 0);

  int m;
  for (m=0; m < dispSteps; m++) {
		written[m] = false;
	}

  writeSynchroniser = sem_open ("writeSyncSem", O_CREAT | O_EXCL, 0644, 1);
  sem_unlink("writeSyncSem");
}

void setupManagementArray() {
  shmMAID = shmget(IPC_PRIVATE, dispSteps*numActions*NUMPROC * sizeof managementImpacts[0], IPC_CREAT | 0700);
  managementImpacts_data = shmat(shmMAID, NULL, 0); //attach for parent
  shmctl (shmMAID , IPC_RMID , 0);
}

void indexManagementArray() {
  /* Index Aggregates for easier access */
	int i,j,k;
  managementImpacts = (int***)malloc(dispSteps * sizeof(int**));

	for (i=0; i < dispSteps; i++) {
		managementImpacts[i] = (int**)malloc(numActions * sizeof(int*));
		for (j=0; j < numActions; j++) {
			managementImpacts[i][j] =  (int*)(managementImpacts_data + (i * numActions * NUMPROC) + (j * NUMPROC));
		}
	}
}

void deIndexManagementArray() {
  int i,j;
  if (managementImpacts != NULL) {
    for (i = 0; i < dispSteps; i++) {
      free(managementImpacts[i]);
    }
    free(managementImpacts);
  }
}

void zeroManagementArray() {
  int i,j,k;

  printf("Zeroing\n");

  for (i=0; i < dispSteps; i++) {
		for (j=0; j < numActions; j++) {
			for (k=0; k < NUMPROC; k++) {
        managementImpacts[i][j][k] = 0;
      }
		}
	}
}

void cleanupStepCompleteArray() {
		/* shared memory detach */
        shmdt ((void *) stepComplete);
        shmctl (stepComplete_shmid, IPC_RMID, 0);

        shmdt ((void *) written);
        shmctl (written_shmid, IPC_RMID, 0);

        /* cleanup semaphores */
        sem_destroy (stepCompleteLock);
        sem_destroy (writeSynchroniser);
}

bool incrementStepComplete(int i) {
  bool summarise = false;
	sem_wait(stepCompleteLock);
    stepComplete[i] += 1;
    if (stepComplete[i] == NUMPROC) {
      summarise = true;
    }
  sem_post(stepCompleteLock);

  return summarise;
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

void readManagementActions(char const *inputDir) {
  char fileName[128];
  managementActions = NULL;

  managementActions = (int **)malloc (nrRows * sizeof (int *));
  for (i = 0; i < nrRows; i++)
  {
      managementActions[i] = (int *)malloc (nrCols * sizeof (int));
  }

  sprintf(fileName, "%s%s.tif", inputDir, "ma");
  readMat(fileName,managementActions);
}

void proc_wait() {
    /* If at process limit, wait for other processes to finish */
    if (procCount >= MAXPROC + 1) {
        //printf("waiting\n");
        if ((wpid = wait(&status)) > 0)
        {
            procCount--;
            printf("Exit status of %d was %d (%s)\n", (int)wpid, status,
                   (status > 0) ? "accept" : "reject");
        }
    }
}
