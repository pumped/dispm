import numpy
import hashlib
from collections import OrderedDict
import csv

class MatrixManager():

	hs = OrderedDict()
	rootPath = ""
	runPath = ""
	hsBufferLength = 20
	parentDict = {}

	currentMatrix = None

	def __init__(self, rootPath = ''):
		#read in parent dictionary
		self.rootPath = rootPath
		self.runPath = rootPath + '/runs'
		self.__readParentDict()
		self.__readInitialMatrix()
		#log.info('Loaded Initial Matrix')

	def __readInitialMatrix(self):
		#read path from config
		path = self.rootPath + '/init/max_pre1.asc'
		m = Matrix(path)
		id = self.checkIdentity(m.matrix)
		m.parent = None
		self.currentMatrix = m
		self.__addHS(id, m) #cache

	def checkIdentity(self, mat):
		return hashlib.sha1(mat).hexdigest()

	#creates new matrice based of the matrice specified
	def createNew(self, parentID):
		self.currentMatrix = Matrix()
		self.currentMatrix.parent = parentID

		#initialise matrix to parent matrix
		parent = getHS()
		self.currentMatrix.matrix = parent.matrix

	#modify matrix
	def setCell(self, coordinates, value):
		pass

	#save the current matrix as a new state
	def save(self):
		pass
		#log.info('Saving State')

	def getHS(self, id):
		if id in self.hs:
			return self.hs.id
		else:
			m = Matrix(self.runPath + str(id) + 'max_pre1.asc')

			#check identity
			id = self.checkIdentity(m.matrix)

			#cache
			self.__addHS(id, m)
			
			return m

	def __addHS(self, id, mat):
		if id in self.hs:
			return 1
		else:
			#check buffer length and pop last item if oversized
			if len(self.hs) > self.hsBufferLength:
				self.hs.popitem()
			self.hs[id] = mat

	def __cachedHS(self, id):
		if id in self.hs:
			return self.hs[id]

	def __readParentDict(self):
		#read parent dictionaries in
		f = self.rootPath + "/parents.csv"
		for key, val in csv.reader(open(f)):
			self.parentDict[key] = val
	
	def __writeParentDict(self):
		#write parent dictionaries file out
		f = self.rootPath + "/parents.csv"
		w = csv.writer(open(f, "w"))
		for key, val in dict.items():
		    w.writerow([key, val])

class Matrix():

	matrix = None
	parent = None
	ncols = 0
	nrows = 0
	xllcorner = 0
	yllcorner = 0
	cellsize = 0.001
	nodataVal = -9999

	def getMatrix(self):
		return self.matrix

	def __init__(self, file=None):
		if file is not None:
			self.readASC(file)

	def readASC(self, file):		
		#read file
		ascArray = numpy.loadtxt(file, skiprows=6)
		self.matrix = numpy.matrix(ascArray)

		#read header
		with open(file, 'r') as f:
			self.ncols = f.readline().split(' ')[-1].rstrip()
			self.nrows = f.readline().split(' ')[-1].rstrip()
			self.xllcorner = f.readline().split(' ')[-1].rstrip()
			self.yllcorner = f.readline().split(' ')[-1].rstrip()
			self.cellsize = f.readline().split(' ')[-1].rstrip()
			self.nodataVal = f.readline().split(' ')[-1].rstrip()

		return self.matrix

	def writeASC(self, file):
		#prepare header
		#TODO: read xll yll cellsize from base file
		header = "ncols %s\n" % self.matrix.shape[1]
		header += "nrows %s\n" % self.matrix.shape[0]
		header += "xllcorner %s\n" % self.xllcorner
		header += "yllcorner %s\n" % self.yllcorner
		header += "cellsize %s\n" % self.cellsize
		header += "NODATA_value %s" % self.nodataVal
		
		#dump numpy matrix to file
		numpy.savetxt(file, self.matrix, header=header, fmt="%1.2f", comments='')