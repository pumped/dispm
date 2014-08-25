
#defines the main controller thread

import threading
import Queue
from Model import ModelManager
from logger import *

class Controller (threading.Thread):

	state = {}
	modelQueue = Queue.Queue()
	model = ModelManager()
	quit = False

	#constructor
	def __init__(self):
		threading.Thread.__init__(self)
		log.debug('Controller Initialised')

	def __del__(self):
		log.debug('Controller Terminated')

	#return the latest log messages
	def getStatus(self):
		return self.modelQueue.qsize()

	#return the state of a specific paramater set
	def getState(self,id):
		pass

	def getCurrentState(self):
		return {"ID":self.model.getCurrentID()}

	#add a new job to the queue
	def addJob(self,job):
		self.modelQueue.put(job)

	#wait for jobs to become available and run them
	def run(self):
		log.debug('Control thread started')

		while True:
			#wait for queue items
			try:
				job = self.modelQueue.get(True, 5)
			except Queue.Empty:
				#no jobs
				pass
			else:
				#do processing
				log.info('Processed Job: ' + str(job))
				status = self.model.runModel(-1)

				if (status):
					log.info('model run completed successfully')
				else:
					log.info('model run failed')


			#exit if quit registered
			if (self.quit):
				break



