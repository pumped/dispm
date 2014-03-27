from logger import *

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