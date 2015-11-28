CC = gcc
CFLAGS = -lm -lpthread -O3 `gdal-config --cflags` `gdal-config --libs`

mig: migclim.c migclim.h migrate.c barriers.c file_io.c genclust.c src_cell.c univ_disp.c validate.c
	$(CC) -O3 -o mig migclim.c $(CFLAGS)
