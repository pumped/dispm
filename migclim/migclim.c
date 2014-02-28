#include "migclim.h"

#include "migrate.c"
#include "file_io.c"
#include "genclust.c"
#include "barriers.c"
#include "univ_disp.c"
#include "src_cell.c"



int main( int argc, char const *argv[] ) {
	/* code */
	char *param = "/home/dylan/Dev/test/migclim/mig_mic_curr_params.txt";
	int nrFiles = 12;

	mcMigrate(&param, &nrFiles);

	return 0;
}