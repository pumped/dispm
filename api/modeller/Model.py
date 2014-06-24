import os
from logger import *
from Config import Config

class ModelManager():
	def __init__(self):
		pass

	#run the model with a specific identifier
	def runModel(self, id):
		try:
			self.__setupDirectory(id)
		except DirectoryExists:
			log.info('directory '+str(id)+' already exists')
			#return 1 #mark as completed already

		self.__writeInputFiles(id)
		self.__setupParamaterFile({'id':id})
		
		print(Config.rootPath)
		

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
		pass

class Model():

	def __init__(self):
		pass

	def runTask(self,id):
		#write out the params file

		#determine a name for this run

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
