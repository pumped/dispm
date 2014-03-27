
#defines the main controller thread

import threading
import Queue
from Model import Model
from logger import *

class Controller (threading.Thread):

	state = {}
	modelQueue = Queue.Queue()
	model = Model()
	quit = False

	#constructor
	def __init__(self):
		threading.Thread.__init__(self)
		log.debug('Controller Initialised')

	def __del__(self):
		log.debug('Controller Terminated')

	def getStatus():
		return self.modelQueue.qsize()

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
				print job

				#do processing
				print 'Processed Job'
				self.model.runTask(1)

			#exit if quit registered
			if (self.quit):
				break



