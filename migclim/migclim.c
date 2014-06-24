#include "migclim.h"

#include "migrate.c"
#include "file_io.c"
#include "genclust.c"
#include "barriers.c"
#include "univ_disp.c"
#include "src_cell.c"



int main( int argc, char const *argv[] ) {
	/* code */
	char *param = "mig_mic_curr/params.txt";
	int nrFiles = 12;

	mcMigrate(&param, &nrFiles);

	return 0;
}
