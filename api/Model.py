
class Model():

	def __init__(self):
		pass

	def runTask(self,id):
		print 'Running Modelling Task with ID: ' + id

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