#include "migclim.h"

#include "migrate.c"
#include "file_io.c"
#include "genclust.c"
#include "barriers.c"
#include "univ_disp.c"
#include "src_cell.c"

// arguments params file, input, output
int main( int argc, char const *argv[] ) {
	if (argc == 4) {
		
		char const *param = argv[1];
		char const *inputDirectory = argv[2];
		char const *outputDirectory = argv[3];
		int nrFiles = 12;

		printf("Using %s\n", param);

		mcMigrate(&param, &nrFiles, inputDirectory, outputDirectory);

		return 0;

	} else {
		
		printf("\n\nInvalid arguments. \nExpected:\nmig [parameter file location] [input location] [output location]\n\n");
		return -1;
		
	}	
}
