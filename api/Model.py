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
from MapArchiver import MapArchiver

class ModelManager():

	matrices = None #matrix manager
	local = True
	STEPCOMPLETE = "stepcomplete"
	STEPWRITTEN = "write"
	MODELCOMPLETE = "modelcomplete"

	def __init__(self):
		self.matrices = MatrixManager.MatrixManager(Config)
		self.statStore = StatManager()
		self.mapGenerator = MapGenerator()
		self.mapGenerator.start()
		self.archiver = MapArchiver()
		self.archiver.start()

	def __del__(self):
		self.mapGenerator.stop()
		self.archiver.stop()

	def stop(self):
		self.mapGenerator.stop()
		self.archiver.stop()

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

		self.__writeInputFiles(ids)
		log.debug('Input files written')
		self.__setupParamaterFile(ids)
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
		#outputPath = Config.rasterPath + '/' + ids["run"]
		outputPath = path + "/aggs/"
		print "outputpath: " + outputPath
		inputPath = path + '/'
		paramPath = path + '/params.txt'

		#set prevention and protection status
		self.statStore.updateTime(ids["species"],ids["timeline"],0,{"prevention":ids["prevention"], "protection":ids["protection"]})

		#if running modelling locally
		if (self.local):
			cmd = "stdbuf -oL " + Config.migExecutable + " " + paramPath + " " + inputPath + " " + outputPath

			print cmd

			#run process
			proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0, shell=True)

			#capture output
			while True:
				output = proc.stdout.readline()

				#exit if process finished
				if output == '' and proc.poll() is not None:
					self.emit('{"event":"model_complete"}')
					break

				#process output
				if output:
					#print output.strip()
					result = self.processOutput(output.strip())
					if result:
						time = result[1]
						speciesID = ids["species"]
						timelineID = ids["timeline"]

						if result[0] == self.STEPCOMPLETE:
							#update stats
							print result[2]
							self.statStore.updateTime(speciesID,timelineID,time,result[2])

							#emit
							state = self.statStore.getTimeline(speciesID,timelineID)
							self.emit('{"event":"timeline_state","data":{"speciesID":"'+speciesID+'","timelineID":"'+timelineID+'","state":'+state+'}}')

						if result[0] == self.STEPWRITTEN:
							runFile = inputPath + "aggs/agg" + time + ".tif"
							renderedFile = Config.rasterPath + ids["run"] + "/agg" + time + ".tif"

							#render map
							#self.mapGenerator.renderFile(runFile,renderedFile)
							self.archiver.convertFile(runFile,renderedFile)

							#emit
							self.emit('{"event":"time_rendered","data":{"speciesID":"'+speciesID+'","timelineID":"'+timelineID+'","time":'+time+'}}')

						if result[0] == self.MODELCOMPLETE:
							pass
							#self.emit('{"event":"model_complete"}')
			#cleanup
			self.cleanupDirectory(path)

		else: #running remotely using dispy
			jobs = []

			cluster = dispy.JobCluster(Config.migExecutable)

			job = cluster.submit(paramPath, inputPath, outputPath);
			n = job()
			log.debug('job %s at %s with %s' % (job.id, job.start_time, n))
			log.info(job.stdout)

	def cleanupDirectory(self,path):
		pass
		os.remove(path + "/ma.tif")
		os.remove(path + "/max_pre1.tif")
		os.remove(path + "/dist_p.tif")

	def processOutput(self,output):
		line = output.lower()

		#process file write completion
		if line.startswith(self.STEPWRITTEN):
			if (":" in line):
				parts = line.split(":",1)

				if len(parts) == 2:
					#determine year number
					fileNumber = parts[0].replace(self.STEPWRITTEN,"").strip(" ")

					#process output
					statsJson = parts[1].strip()
					stats = json.loads(statsJson)
					# print statsJson

					return [self.STEPWRITTEN,fileNumber, stats]

		if line.startswith(self.STEPCOMPLETE):
			if (":" in line):
				parts = line.split(":",1)

				if len(parts) == 2:
					#determine year number
					fileNumber = parts[0].replace(self.STEPCOMPLETE,"").strip(" ")

					#process output
					statsJson = parts[1].strip()
					stats = json.loads(statsJson)

					return [self.STEPCOMPLETE,fileNumber, stats]
		if line.startswith(self.MODELCOMPLETE):
			return [self.MODELCOMPLETE,0]

	def getDataPath(self):
		return Config.dataPath + 'siam'

	def __setupParamaterFile(self, settings):
		newPath = Config.runPath + '/' + settings['run'] + '/params.txt'
		fInit = open (Config.paramsFilePath, "r")
		fNew = open(newPath, "w")

		print settings

		for line in fInit:
			if (line.startswith("fullOutput")):
				if (settings["full"] == "1"):
					fNew.write("fullOutput true\n")
				if (settings["full"] == "0"):
					fNew.write("fullOutput false\n")
			elif (line.startswith("lddFreq")):
				print settings["prevention"]
				if (settings["prevention"] == "20"):
					fNew.write("lddFreq 0.05\n")
				if (settings["prevention"] == "10"):
					fNew.write("lddFreq 0.08\n")
				if (settings["prevention"] == "0"):
					fNew.write("lddFreq 0.1\n")
			else:
				fNew.write(line)

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

	def __writeInputFiles(self, ids):
		dest = Config.runPath + '/' + str(ids['run'])

		#write out distribution files
		src = Config.initialFiles + '/dist_p.asc'
		dmDest = dest + '/dist_p.asc'

		#run async, export current distribution
		distTifPath = dest+'/dist_p.tif'
		distAscPath = dest+"/dist_p.asc"
		distCmd = 'gdal_rasterize -burn 1 -a_nodata 0 -init 0 -te 143.9165675170000043 -20.0251072599999986 147.0005675170000075 -14.9801072599999987 -ts 3084 5045 -a_srs "EPSG:3857" PG:"host=localhost user=postgres dbname=nyc password=password1" -sql "SELECT * FROM distribution WHERE species = \'siam\'" -of GTiff '+distTifPath
		#distCmd += " ; "
		#distCmd += "gdal_translate -a_nodata -9999 -of AAIGrid "+distTifPath+" "+distAscPath
		proc = subprocess.Popen(distCmd, stdout=subprocess.PIPE, bufsize=0, shell=True)

		#rasterize Control Mechanisms
		adjustTifPath = dest+'/ma.tif'
		status = subprocess.call('gdal_rasterize -a "controlMechanism" -a_nodata -9999 -init -9999 -te 143.9165675170000043 -20.0251072599999986 147.0005675170000075 -14.9801072599999987 -ts 3084 5045 -a_srs "EPSG:3857" PG:"host=localhost user=postgres dbname=nyc password=password1" -sql "SELECT * FROM nyc_buildings WHERE timeline = \''+ids['timeline']+'\'" -of GTiff '+adjustTifPath, shell=True)

		#translate to AAIGrid
		#maxPath = dest+'/ma.asc'
		#status = subprocess.call('gdal_translate -a_nodata -9999 -of AAIGrid '+adjustTifPath+' '+maxPath, shell=True)
		#
		# #cleanup intermediary files
		# os.remove(mergedTifPath)
		#os.remove(adjustTifPath)

		#wait for distribution to finish
		while True:
			output = proc.stdout.readline()
			if output == '' and proc.poll() is not None:
				print "finished"
				break
			if output:
				print output

		#cleanup intermediary file
		#os.remove(distTifPath)

		#copy initial distribution map over
		src = Config.initialFiles + '/max_pre1.tif'
		dmDest = dest + '/max_pre1.tif'
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
