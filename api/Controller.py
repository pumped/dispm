
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
	emitCallback = None

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

	def makeID(self, species, timeline):
		return str(species) + "-" + str(timeline)

	#add a new job to the queue
	def addJob(self,job):
		self.modelQueue.put(job)

	def stop(self):
		self.model.stop()
		self.quit = True

	def onMessage(self, func):
		self.emitCallback = func
		self.model.onMessage(func)

	def _emit(self, message):
		if self.emitCallback:
			self.emitCallback(message)

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
				status = self.model.runModel(str(job))

				if (status):
					log.info('model run completed successfully')
				else:
					log.info('model run failed')


			#exit if quit registered
			if (self.quit):
				break
