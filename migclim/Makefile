CC = gcc
CFLAGS = -lm -lpthread

mig: migclim.c migclim.h migrate.c barriers.c file_io.c genclust.c src_cell.c univ_disp.c validate.c
	$(CC) -O3 -o mig migclim.c $(CFLAGS)
