/*
** file_io.c: Functions for file input/output.
**
** Wim Hordijk   Last modified: 11 May 2012 (RE)
*/

#include "migclim.h"

#include "gdal.h"
#include "ogr_core.h"
#include "ogr_srs_api.h"
#include "cpl_conv.h" /* for CPLMalloc() */
#include "cpl_string.h"

#include <time.h>


/*
** mcInit: Initialize the MigClim model by reading the parameter values from
**         file.
**
** Parameters:
**   - paramFile: The name of the file from which to read the parameter values.
**
** Returns:
**   - If everything went fine:  0.
**   - Otherwise:               -1.
*/

int mcInit (char const *paramFile)
{
  int    i, age, status, lineNr;
  char   line[1024], param[64];
  float  p;
  FILE  *fp;

  status = 0;
  fp = NULL;

  /*
  ** Set default parameter values.
  */
  nrRows = 0;
  nrCols = 0;
  strcpy (iniDist, "");
  strcpy (hsMap, "");
  strcpy (barrier, "");
  useBarrier = false;
  barrierType = STRONG_BARRIER;
  envChgSteps = 0;
  dispSteps = 0;
  dispDist = 0;
  iniMatAge = 0;
  fullMatAge = 0;
  rcThreshold = 0;
  lddMinDist = 10;
  lddMaxDist = 15;
  lddFreq = 0.0;
  fullOutput = false;
  replicateNb = 1;
  strcpy (simulName, "MigClimTest");

  /*
  ** Open the file for reading.
  */
  if ((fp = fopen(paramFile, "r")) == NULL)
  {
    status = -1;
    printf ("Can't open parameter file %s\n", paramFile);
    goto End_of_Routine;
  }

  /*
  ** While there are lines left, read and parse them.
  */
  lineNr = 0;
  param[0] = '\0';
  while (fgets (line, 1024, fp) != NULL)
  {
    lineNr++;
    sscanf (line, "%s", param);
    /* nrRows */
    if (strcmp (param, "nrRows") == 0)
    {
      if ((sscanf (line, "nrRows %d", &nrRows) != 1) || (nrRows < 1))
      {
	status = -1;
	printf ("Invalid number of rows on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* nrCols */
    else if (strcmp (param, "nrCols") == 0)
    {
      if ((sscanf (line, "nrCols %d", &nrCols) != 1) || (nrCols < 1))
      {
	status = -1;
	printf ("Invalid number of columns on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* iniDist */
    else if (strcmp (param, "iniDist") == 0)
    {
      if (sscanf (line, "iniDist %s", iniDist) != 1)
      {
	status = -1;
	printf ("Invalid initial distribution file name on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* hsMap */
    else if (strcmp (param, "hsMap") == 0)
    {
      if (sscanf (line, "hsMap %s", hsMap) != 1)
      {
	status = -1;
	printf ("Invalid habitat suitability map file name on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* barrier */
    else if (strcmp (param, "barrier") == 0)
    {
      if (sscanf (line, "barrier %s", barrier) != 1)
      {
	status = -1;
	printf ("Invalid barrier file name on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      useBarrier = true;
    }
    /* barrierType */
    else if (strcmp (param, "barrierType") == 0)
    {
      if (sscanf (line, "barrierType %s", param) != 1)
      {
	status = -1;
	printf ("Invalid barrier type on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      if (strcmp (param, "weak") == 0)
      {
	barrierType = WEAK_BARRIER;
      }
      else if (strcmp (param, "strong") == 0)
      {
	barrierType = STRONG_BARRIER;
      }
      else
      {
	status = -1;
	printf ("Invalid barrier type on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* envChgSteps */
    else if (strcmp (param, "envChgSteps") == 0)
    {
      if ((sscanf (line, "envChgSteps %d", &envChgSteps) != 1) ||
	  (envChgSteps < 1))
      {
	status = -1;
	printf ("Invalid number of environmental change steps on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* dispSteps */
    else if (strcmp (param, "dispSteps") == 0)
    {
      if ((sscanf (line, "dispSteps %d", &dispSteps) != 1) ||
	  (dispSteps < 1))
      {
	status = -1;
	printf ("Invalid number of dispersal steps on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* dispDist & dispKernel */
    else if (strcmp (param, "dispDist") == 0)
    {
      if ((sscanf (line, "dispDist %d", &dispDist) != 1) ||
	  (dispDist < 1))
      {
	status = -1;
	printf ("Invalid dispersal distance on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      lineNr++;
      dispKernel = (double *)malloc (dispDist * sizeof (double));
      if (fscanf (fp, "dispKernel %f", &p) != 1)
      {
	status = -1;
	printf ("Dispersal kernel expected on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      dispKernel[0] = p;
      for (i = 1; i < dispDist; i++)
      {
	if (fscanf (fp, "%f", &p) != 1)
	{
	  status = -1;
	  printf ("Invalid dispersal kernel values on line %d in parameter file %s.\n",
		   lineNr, paramFile);
	  goto End_of_Routine;
	}
	dispKernel[i] = p;
      }
      p = fscanf (fp, "\n");
    }
    /* iniMatAge */
    else if (strcmp (param, "iniMatAge") == 0)
    {
      if ((sscanf (line, "iniMatAge %d", &iniMatAge) != 1) ||
	  (iniMatAge < 1))
      {
	status = -1;
	printf ("Invalid initial maturity age on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* fullMatAge */
    else if (strcmp (param, "fullMatAge") == 0)
    {
      if ((sscanf (line, "fullMatAge %d", &fullMatAge) != 1) ||
	  (fullMatAge < 1))
      {
	status = -1;
	printf ("Invalid full maturity age on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      lineNr++;
      age = fullMatAge - iniMatAge;
      if (age == 0)
      {
	age = 1;
      }
      propaguleProd = (double *)malloc (age * sizeof (double));
      if (fscanf (fp, "propaguleProd %f", &p) != 1)
      {
	status = -1;
	printf ("Seed production probabilities expected on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      propaguleProd[0] = p;
      for (i = 1; i < age; i++)
      {
	if (fscanf (fp, "%f", &p) != 1)
	{
	  status = -1;
	  printf ("Invalid seed production probability on line %d in parameter file %s\n",
		   lineNr, paramFile);
	  goto End_of_Routine;
	}
	propaguleProd[i] = p;
      }
      p = fscanf (fp, "\n");
    }
    /* rcThreshold */
    else if (strcmp (param, "rcThreshold") == 0)
    {
      if ((sscanf (line, "rcThreshold %d", &rcThreshold) != 1) ||
	  (rcThreshold < 0) || (rcThreshold > 1000))
      {
	status = -1;
	printf ("Invalid reclassification threshold on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* lddFreq */
    else if (strcmp (param, "lddFreq") == 0)
    {
      if ((sscanf (line, "lddFreq %f", &p) != 1) ||
	  (p < 0.0) || (p > 1.0))
      {
	status = -1;
	printf ("Invalid long-distance dispersal frequency on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      lddFreq = p;
    }
    /* lddMinDist */
    else if (strcmp (param, "lddMinDist") == 0)
    {
      if ((sscanf (line, "lddMinDist %d", &lddMinDist) != 1) || (lddMinDist < 0))
      {
	status = -1;
	printf ("Invalid minimum long-distance dispersal value on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* lddMaxDist */
    else if (strcmp (param, "lddMaxDist") == 0)
    {
      if ((sscanf (line, "lddMaxDist %d", &lddMaxDist) != 1) || (lddMaxDist <= lddMinDist))
      {
	status = -1;
	printf ("Invalid maximum long-distance dispersal value on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* fullOutput */
    else if (strcmp (param, "fullOutput") == 0)
    {
      if (sscanf (line, "fullOutput %s", param) != 1)
      {
	status = -1;
	printf ("Incomplete 'fullOutput' argument on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
      if (strcmp (param, "true") == 0)
      {
	fullOutput = true;
      }
      else if (strcmp (param, "false") == 0)
      {
	fullOutput = false;
      }
      else
      {
	status = -1;
	printf ("Invalid value for argument 'fullOutput' on line %d in parameter file %s\n", lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* replicateNb */
    else if (strcmp (param, "replicateNb") == 0)  /* if both strings are equal, strcmp returns 0 */
    {
      if(sscanf(line, "replicateNb %d", &replicateNb) != 1)  /* On success, the function returns the number of variables filled.  */
      {
	    status = -1;
	    printf ("Invalid value for replicateNb parameter on line %d in parameter file %s\n", lineNr, paramFile);
	    goto End_of_Routine;
      }
    }

    /* simulName */
    else if (strcmp (param, "simulName") == 0)
    {
      if (sscanf (line, "simulName %s", simulName) != 1)
      {
	status = -1;
	printf ("Invalid output file name on line %d in parameter file %s\n",
		 lineNr, paramFile);
	goto End_of_Routine;
      }
    }
    /* Unknown parameter */
    else
    {
      status = -1;
      printf ("Unknown parameter on line %d in parameter file %s\n", lineNr,
	      paramFile);
      goto End_of_Routine;
    }
  }

  /*
  ** Check the parameter values for validity.
  */
  if (nrRows == 0)
  {
    status = -1;
    printf ("No number of rows specified in parameter file %s\n", paramFile);
    goto End_of_Routine;
  }
  if (nrCols == 0)
  {
    status = -1;
    printf ("No number of columns specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (strlen (iniDist) == 0)
  {
    status = -1;
    printf ("No initial distribution file name specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (strlen (hsMap) == 0)
  {
    status = -1;
    printf ("No habitat suitability map file name specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (useBarrier && (strlen (barrier) == 0))
  {
    status = -1;
    printf ("No barrier file name specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (envChgSteps == 0)
  {
    status = -1;
    printf ("No number of environmental change steps specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (dispSteps == 0)
  {
    status = -1;
    printf ("No number of dispersal steps specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (dispDist == 0)
  {
    status = -1;
    printf ("No dispersal distance specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (iniMatAge == 0)
  {
    status = -1;
    printf ("No initial maturity age specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }
  if (fullMatAge == 0)
  {
    status = -1;
    printf ("No full maturity age specified in parameter file %s\n",
	     paramFile);
    goto End_of_Routine;
  }

 End_of_Routine:
  /*
  ** Close the file and return the status.
  */
  if (fp != NULL)
  {
    fclose (fp);
  }
  return (status);
}


/*
** readMat: Read a data matrix from an ESRI ascii grid file.
**
** Note: This should eventually be merged with the above "mcReadMatrix"
**       function, but we'll keep it separate for now just to make sure
**       the basic functionality works fine.
**
** Parameters:
**   - fName:  The name of the file to read from.
**   - mat:    The matrix to put the data in (assumed to be large enough).
**
** Returns:
**   - If everything went fine:  0.
**   - Otherwise:               -1.
*/

int readMat (char *fName, int **mat)
{
  int   i, j, intVal, status;
  char  line[1024], param[128], dblVal[128];
  FILE *fp;

  status = 0;
  fp = NULL;

  GDALDatasetH  hDataset;

  hDataset = GDALOpen( fName, GA_ReadOnly );
  if( hDataset == NULL )
  {
    printf("Dataset Not Found \n");
    status = -1;
  } else {

    //save georeference
    GDALGetGeoTransform( hDataset, adfGeoTransform );

    projection = GDALGetProjectionRef( hDataset );
    //printf( "Projection is `%s'\n", projection );

    //get band
    GDALRasterBandH hBand;
    hBand = GDALGetRasterBand( hDataset, 1 );

    //load band metadata
    int *pafScanline;
    int   nXSize = GDALGetRasterBandXSize( hBand );
    int   nYSize = GDALGetRasterBandYSize( hBand );

    if (nrCols != nXSize || nrRows != nYSize) {
      return -1;
    }

    pafScanline = (int *) CPLMalloc(sizeof(int)*nXSize);
    int i,j;
    //for each scanline
    for (i=0; i<nYSize; i++) {
      // load scanline into memory
      GDALRasterIO( hBand, GF_Read, 0, i, nXSize, 1,
                    pafScanline, nXSize, 1, GDT_Int32,
                    0, 0 );

      //foreach item in scanline
      for (j=0; j<nXSize; j++) {
        //if (pafScanline[j] > 0) {
          mat[i][j] = pafScanline[j];
          //printf("%i ", pafScanline[j]);
        //}
      }
    }
    CPLFree(pafScanline);

    //close dataset
    GDALClose(hDataset);
  }

  return (status);
}


/*
** writeMat: Write a data matrix to file.
**
** Note: This should eventually be merged with the above "mcWriteMatrix"
**       function, but we'll keep it separate for now just to make sure
**       the basic functionality works fine.
**
** Parameters:
**   - fName:  The name of the file to write to.
**   - mat:    The data matrix to write.
**
** Returns:
**   - If everything went fine:  0.
**   - Otherwise:               -1.
*/

int writeMat (char *fName, int **mat)
{
  int   i, j, status;
  status = 0;

  clock_t begin, end;
  double time_spent;
  begin = clock();

  const char *pszFormat = "GTiff";
  GDALDriverH hDriver = GDALGetDriverByName( pszFormat );

  //get size
  int   nXSize = nrCols;
  int   nYSize = nrRows;

  //set options
  GDALDatasetH hDstDS;
  char **papszOptions = NULL;
  papszOptions = CSLSetNameValue( papszOptions, "COMPRESS", "DEFLATE" );

  //create gtiff
  hDstDS = GDALCreate( hDriver, fName, nXSize, nYSize, 1, GDT_Int32, papszOptions );

  //set transform
  GDALSetGeoTransform( hDstDS, adfGeoTransform );
  projection = "PROJCS[\"WGS 84 / Pseudo-Mercator\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0],UNIT[\"degree\",0.0174532925199433],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Mercator_1SP\"],PARAMETER[\"central_meridian\",0],PARAMETER[\"scale_factor\",1],PARAMETER[\"false_easting\",0],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],EXTENSION[\"PROJ4\",\"+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs\"],AUTHORITY[\"EPSG\",\"3857\"]]'";
  GDALSetProjection( hDstDS, projection );
  //printf( "Projection is `%s'\n", projection );

  //setup bands
  GDALRasterBandH hBand;
  hBand = GDALGetRasterBand( hDstDS, 1 );


  end = clock();
  time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
  printf("Create Time: %f \n",time_spent);

  //for each scanline
  for (i=0; i<nYSize; i++) {
     GDALRasterIO( hBand, GF_Write, 0, i, nXSize, 1,
                   mat[i], nXSize, 1, GDT_Int32,
                   0, 0 );
  }

  /* Once we're done, close properly the dataset */
  if( hDstDS != NULL )
      GDALClose( hDstDS );

  end = clock();
  time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
  printf("Total Time: %f \n",time_spent);

  /*
  ** Close the file and return the status.
  */
 End_of_Routine:
  return (status);
}


/*
** EoF: file_io.c
*/
