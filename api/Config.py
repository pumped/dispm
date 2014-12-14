
class Config():

	#debug
	debug = True

	#Paths
	rootPath = '/home/dylan/dev/test/api'
	scratchPath = '/home/dylan/dev/test/scratch'
	initialFiles = rootPath + '/init'
	currentFiles = scratchPath + '/current'
	runPath = scratchPath + '/runs'
	aggregatesPath = '/aggs'
	migExecutable = '/home/dylan/Dev/test/api/init/mig'

	paramsFilePath = initialFiles + '/params.txt'
	initHS = initialFiles + '/max_pre1.asc'
	hsFile = currentFiles + '/max_pre1.asc'


	#Repetitions
	repetitions = 2