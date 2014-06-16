from MatrixManager import MatrixManager

m = MatrixManager("/home/pumped/Development/phd/test/api")
mat = m.readASC('/home/pumped/Development/phd/test/api/runs/asd88348asd/max_pre1.asc')
m.writeASC(mat, '/home/pumped/Development/phd/test/api/runs/asd88348asd/max_pre3.asc')