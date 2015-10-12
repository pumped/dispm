import os
from logger import *
from Config import Config
from mat import MatrixManager
import shutil
import dispy
import subprocess

class ModelManager():

	matrices = None #matrix manager
	matrixID = 0 #current matrix identifier
	local = True

	def __init__(self):
		self.matrices = MatrixManager.MatrixManager(Config)

	#run the model with a specific identifier
	def runModel(self, id):
		#default id to current if non existant
		if (id == -1):
			id = self.getCurrentID(True)
			log.info('Identifier Defaulted to: ' + str(id))

		try:
			self.__setupDirectory(id)
		except DirectoryExists:
			log.info('directory '+str(id)+' already exists')
			if not Config.debug:
				return 0 #mark as completed already

		self.__writeInputFiles(id)
		log.debug('Input files written')
		self.__setupParamaterFile({'id':id})
		log.debug('Paramater files written')

		# #run model on dispy node
		self.__runModelJob(id)

		return 1

	def setMatrix(self, id):
		self.matrixID = id

	def getState(self,id):
		pass

	def getCurrentID(self, force=False):
		return self.matrices.checkIdentity(force)


	#run the model executable and process output
	def __runModelJob(self, id):
		log.info('Model Kicked off')
		path = Config.runPath + '/' + id
		outputPath = path + Config.aggregatesPath
		inputPath = path + '/'
		paramPath = path + '/params.txt'

		#if running modelling locally
		if (self.local):
			cmd = "stdbuf -oL " + Config.migExecutable + " " + paramPath + " " + inputPath + " " + outputPath

			#run process
			proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0, shell=True)

			#capture output
			while True:
				output = proc.stdout.readline()
				if output == '' and proc.poll() is not None:
					break
				if output:
					self.processOutput(output.strip())

			print "Process Finished"
		else: #running remotely using dispy
			jobs = []

			cluster = dispy.JobCluster(Config.migExecutable)

			job = cluster.submit(paramPath, inputPath, outputPath);
			n = job()
			log.debug('job %s at %s with %s' % (job.id, job.start_time, n))
			log.info(job.stdout)

	def processOutput(output):
	    line = output.lower()

	    #process file write completion
	    if line.startswith("write"):
	        if (":" in line):
	            parts = line.split(":",1)

	            if len(parts) == 2:
	                #determine year number
	                fileNumber = parts[0].replace("write","").strip(" ")

	                #process output
	                statsJson = parts[1].strip()
                	stats = json.loads(statsJson)

	                return [fileNumber, stats]

	def getDataPath(self):
		return Config.dataPath + 'siam'

	def __setupParamaterFile(self, settings):
		newPath = Config.runPath + '/' + settings['id'] + '/params.txt'
		fInit = open (Config.paramsFilePath, "r")
		fNew = open(newPath, "w")
		fNew.write(fInit.read())
		fInit.close()
		fNew.close()

	def __setupDirectory(self, id):
		path = Config.runPath + '/'+str(id)
		if not os.path.exists(path):
			os.makedirs(path)
			outputPath = path + Config.aggregatesPath
			if not os.path.exists(outputPath):
				os.makedirs(outputPath)
		else:
			raise DirectoryExists

	def __writeInputFiles(self, id):
		dest = Config.runPath + '/' + str(id)

		#rasterize Control Mechanisms
		status = subprocess.call('gdal_rasterize -a "controlMechanism" -a_nodata -9999 -init -9999 -te 143.9165675170000043 -20.0251072599999986 147.0005675170000075 -14.9801072599999987 -ts 3084 5045 PG:"host=localhost user=postgres dbname=nyc password=password1" -sql "SELECT * FROM nyc_buildings WHERE time >= 0" -of GTiff '+dest+'/adjust.tif', shell=True)
		print status

		#merge rasters
		status = subprocess.call('gdal_merge.py -a_nodata -9999 -n -9999 '+self.getDataPath()+'/max_pre1.tif '+dest+'/adjust.tif -o '+dest+'/merged.tif', shell=True)

		#translate to AAIGrid
		status = subprocess.call('gdal_translate -a_nodata -9999 -of AAIGrid '+dest+'/merged.tif '+dest+'/max_pre1.asc', shell=True)

		#copy hs to folder
		#src = Config.hsTif
		#dmDest = dest + '/max_pre1.tif'
		#shutil.copyfile(src,dmDest)

		#copy initial distribution map over
		src = Config.initialFiles + '/dist_p.asc'
		dmDest = dest + '/dist_p.asc'
		shutil.copyfile(src,dmDest)


class Model():

	def __init__(self):
		pass

	def runTask(self,id):
		#run the simulation
		log.info('Running Modelling Task with ID: ' + str(id))

	def killTask(self):
		pass

	def estimateRemaining(self):
		pass

	def status(self):
		return 'idle'


class DirectoryExists(Exception):
	pass

class AlreadyRun(Exception):
	pass
