import os
from logger import *
from Config import Config
from mat import MatrixManager
import shutil

class ModelManager():

	matrices = None #matrix manager
	matrixID = 0 #current matrix identifier

	def __init__(self):
		self.matrices = MatrixManager.MatrixManager(Config.rootPath)

	#run the model with a specific identifier
	def runModel(self, id):
		#default id to current
		if (id == -1):
			id = self.matrices.checkIdentity((self.matrices.currentMatrix.matrix))
			log.info('Identifier Defaulted to: ' + str(id))

		try:
			self.__setupDirectory(id)
		except DirectoryExists:
			log.info('directory '+str(id)+' already exists')
			return 1 #mark as completed already

		self.__writeInputFiles(id)
		log.debug('Input files written')
		self.__setupParamaterFile({'id':id})
		log.debug('Paramater files written')
		
		
		

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
		else:
			raise DirectoryExists

	def __writeInputFiles(self, id):
		dest = Config.runPath + '/' + str(id)
		
		#write habitat suitability
		self.matrices.currentMatrix.writeASC(dest + '/max_pre1.asc')
		
		#copy initial distribution map over
		src = Config.initialFiles + '/dist_p.asc'
		dmDest = dest + '/dist_p.asc'
		shutil.copyfile(src,dmDest)

		#copy mig over
		src = Config.initialFiles + '/mig'
		migDest = dest + '/mig'
		shutil.copyfile(src,migDest)



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

class Tiler():

	def __init__(self):
		pass

	def status(self):
		return 'running'



class DirectoryExists(Exception):
	pass

class AlreadyRun(Exception):
	pass
