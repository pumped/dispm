/*
** migclim.h: Header file for the MigClim methods.
** Wim Hordijk   Last modified: 11 May 2012 (RE)
*/

#ifndef _MIGCLIM_H_
#define _MIGCLIM_H_

/*
** Include files.
*/
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include <math.h>

#include <sys/types.h>      /* key_t, sem_t, pid_t      */
#include <sys/shm.h>        /* shmat(), IPC_RMID        */
#include <semaphore.h>      /* sem_open(), sem_destroy(), sem_wait().. */
#include <fcntl.h>



/*
** Defines.
**
** UNIF01:         Draw a uniform random number in [0;1]. Note that 'random'
**                 does not work on Windows %-/  so we use 'rand' instead.
** WEAK_BARRIER:   Weak barrier type.
** STRONG_BARRIER: Strong barrier type.
*/
#define UNIF01         ((double)rand () / RAND_MAX)
#define WEAK_BARRIER   1
#define STRONG_BARRIER 2

#define DELIMITATION 0
#define PREVENTION 1
#define REMOVAL 2
#define CONTAINMENT 3
#define IMPACT_CONTROL 4
#define ASSET_PROTECTION 5

/*
** Global variables (we just use many global var's here to avoid passing too
** many arguments all the time).
*/

extern int     nrRows, nrCols, envChgSteps, dispSteps, dispDist, iniMatAge,
               fullMatAge, rcThreshold, barrierType, lddMinDist, lddMaxDist,
               noData, replicateNb;
extern double *dispKernel, *propaguleProd, lddFreq, xllCorner, yllCorner,
               cellSize;
extern char    iniDist[128], hsMap[128], simulName[128], barrier[128];
extern bool    useBarrier, fullOutput;

int ***aggregates;
int *aggregates_data;
int shmid2;
int **managementActions;

key_t stepComplete_shmkey;
int stepComplete_shmid;
sem_t *stepCompleteLock;
int *stepComplete;

key_t written_shmkey;
int written_shmid;
sem_t *writeSynchroniser;
int *written;

int procID;

/*
** Function prototypes.
*/
void mcMigrate           (char const **paramFile, int *nrFiles, char const *inputDir, char const *outputDir);
bool mcSrcCell           (int i, int j, int **curState, int **pxlAge,
			  int loopID, int habSuit, int **barriers, int *last);
int  mcUnivDispCnt       (int **habSuit);
void updateNoDispMat     (int **hsMat, int **noDispMat, int *noDispCount);
void mcFilterMatrix      (int **inMatrix, int **filterMatrix, bool filterNoData, bool filterOnes, bool insertNoData);
bool mcIntersectsBarrier (int snkX, int snkY, int srcX, int srcY, int **barriers);
int  mcInit              (char const *paramFile);
int  readMat             (char *fName, int **mat);
int  writeMat            (char *fName, int **mat);
void genClust            (int *nrow, int *ncol, int *ncls, int *niter, int *thrs, char **suitBaseName,
                          char **barrBaseName, char **outBaseName, char **initFile);
void validate            (char **obsFileName, int *npts, char **simFileName, int *ncls, double *bestScore);
int main 				 (int argc, char const *argv[]);

void writeAggregateFile	 (int matID, char const *outputDirectory);
void writeLock			 (char const *lockPath);
int sum             (int matID);

void deleteLock			 (char const *lockPath);

void proc_wait();
void indexAggregates();
void deIndexAggregates();
void zeroAggregates();

void readManagementActions(char const *inputDir);
bool checkSuitability(int i, int j, bool ldd);
bool srcPixel(int srcX, int srcY, int tX, int tY, int dispStep, bool ldd);
void removeInitial(int **currentState, int year);
int cellAction(int srcX, int srcY, int year);
int getTimeFromActionString(int code);

int shmMAID;
int ***managementImpacts;
int *managementImpacts_data;
void setupStepCompleteArray();
void cleanupStepCompleteArray();
bool incrementStepComplete(int i);
void setupManagementArray();
void indexManagementArray();
void deIndexManagementArray();
void zeroManagementArray();

void writeThread();


#endif  /* _MIGCLIM_H_ */

/*
** EoF: migclim.h
*/
