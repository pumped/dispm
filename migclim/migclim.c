#include "migclim.h"

#include "migrate.c"
#include "file_io.c"
#include "genclust.c"
#include "barriers.c"
#include "univ_disp.c"
#include "src_cell.c"



int main( int argc, char const *argv[] ) {
	/* code */
<<<<<<< HEAD
	char *param = "/home/dylan/Dev/test/migclim/mig_mic_curr_params.txt";
=======
	char *param = "mig_mic_curr/mig_mic_curr_params.txt";
>>>>>>> 0ddc324f68d89211a3446bb4c0dae1b81d3cb718
	int nrFiles = 12;

	mcMigrate(&param, &nrFiles);

	return 0;
}
