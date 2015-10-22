import os
from logger import *
from Config import Config
from mat import MatrixManager
import shutil
import dispy
import subprocess
import json
from DataStore import StatManager
from MapRenderer import MapGenerator

class ModelManager():

	matrices = None #matrix manager
	local = True

	def __init__(self):
		self.matrices = MatrixManager.MatrixManager(Config)
		self.statStore = StatManager()
		self.mapGenerator = MapGenerator()
		self.mapGenerator.start()

	def __del__(self):
		self.mapGenerator.stop()

	def stop(self):
		self.mapGenerator.stop()

	#run the model with a specific identifier
	def runModel(self, ids):
		#default id to current if non existant
		if (ids == None):
			id = self.getCurrentID(True)
			log.error('Identifier Defaulted to: ' + str(id))

		try:
			self.__setupDirectory(str(ids["run"]))
		except DirectoryExists:
			log.info('directory '+str(ids["run"])+' already exists')
			if not Config.debug:
				return 0 #mark as completed already

		self.__writeInputFiles(ids["run"])
		log.debug('Input files written')
		self.__setupParamaterFile({'id':ids["run"]})
		log.debug('Paramater files written')

		# #run model
		self.__runModelJob(ids)

		return 1

	def getState(self,id):
		pass

	def getCurrentID(self, force=False):
		return self.matrices.checkIdentity(force)

	def emit(self,message):
		if self.emitCallback:
			self.emitCallback(message)

	def onMessage(self, func):
		self.emitCallback = func


	#run the model executable and process output
	def __runModelJob(self, ids):
		log.info('Model Kicked off')
		path = Config.runPath + '/' + ids["run"]
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
					result = self.processOutput(output.strip())
					if result:
						time = result[0]
						runFile = inputPath + "aggs/agg" + time + ".asc"
						renderedFile = Config.renderedPath + ids["run"] + "/agg" + time + ".png"

						speciesID = ids["species"]
						timelineID = ids["timeline"]

						#render map
						self.mapGenerator.renderFile(runFile,renderedFile)

						#update stats
						self.statStore.updateTime(speciesID,timelineID,time,result[1])

						#emit
						state = self.statStore.getTimeline(speciesID,timelineID)
						self.emit('{"event":"timeline_state","data":{"speciesID":"'+speciesID+'","timelineID":"'+timelineID+'","state":'+state+'}}')

		else: #running remotely using dispy
			jobs = []

			cluster = dispy.JobCluster(Config.migExecutable)

			job = cluster.submit(paramPath, inputPath, outputPath);
			n = job()
			log.debug('job %s at %s with %s' % (job.id, job.start_time, n))
			log.info(job.stdout)

	def processOutput(self,output):
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
		status = subprocess.call('gdal_rasterize -a "controlMechanism" -a_nodata -9999 -init -9999 -te 143.9165675170000043 -20.0251072599999986 147.0005675170000075 -14.9801072599999987 -ts 3084 5045 -a_srs "EPSG:3857" PG:"host=localhost user=postgres dbname=nyc password=password1" -sql "SELECT * FROM nyc_buildings WHERE time >= 0" -of GTiff '+dest+'/adjust.tif', shell=True)
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
