import os
from logger import *
from Config import Config
from mat import MatrixManager
import shutil
import dispy

class ModelManager():

	matrices = None #matrix manager
	matrixID = 0 #current matrix identifier

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

		#run model on dispy node
		self.__runModelJob(id)

		return 1

	def setMatrix(self, id):
		self.matrixID = id

	def getState(self,id):
		pass

	def getCurrentID(self, force=False):
		return self.matrices.checkIdentity(force)

	def __runModelJob(self, id):
		log.info('Model Kicked off')
		jobs = []
		path = Config.runPath + '/' + id
		outputPath = path + Config.aggregatesPath
		inputPath = path + '/'
		paramPath = path + '/params.txt'

		cluster = dispy.JobCluster(Config.migExecutable)

		job = cluster.submit(paramPath, inputPath, outputPath);
		n = job()
		log.debug('job %s at %s with %s' % (job.id, job.start_time, n))
		log.info(job.stdout)

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
		
		#copy hs to folder
		src = Config.hsFile
		dmDest = dest + '/max_pre1.asc'
		shutil.copyfile(src,dmDest)
		
		#copy initial distribution map over
		src = Config.initialFiles + '/dist_p.asc'
		dmDest = dest + '/dist_p.asc'
		shutil.copyfile(src,dmDest)

		#copy mig over
		# src = Config.initialFiles + '/mig'
		# migDest = dest + '/mig'
		# shutil.copyfile(src,migDest)
		# shutil.copystat(src,migDest)



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
