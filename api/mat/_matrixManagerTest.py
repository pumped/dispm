from MatrixManager import *
import unittest
import numpy
import os

class Matrix_test(unittest.TestCase):
	def setUp(self):
		pass

	def testRead(self):
		#write test file
		matrix = numpy.matrix("1,2,3;4,5,6;7,8,9")

		file = "matTestASCGrid.test"

		header = "ncols 3\n"
		header += "nrows 3\n"
		header += "xllcorner 1\n"
		header += "yllcorner 1\n"
		header += "cellsize 1\n"
		header += "NODATA_value -9999"
		
		#dump numpy matrix to file
		numpy.savetxt(file, matrix, header=header, fmt="%1.2f", comments='')

		#test read
		m = Matrix(file)

		assert numpy.array_equiv(m.matrix, matrix), 'Invalid Matricie read in'
		os.remove(file)

	def testOther(self):		
		m = MatrixManager("/home/pumped/Development/phd/test/api")
		mat = m.readASC('/home/pumped/Development/phd/test/api/runs/asd88348asd/max_pre1.asc')
		m.writeASC(mat, '/home/pumped/Development/phd/test/api/runs/asd88348asd/max_pre3.asc')




if __name__ == '__main__':
    unittest.main()