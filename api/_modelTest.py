from Model import ModelManager

m = ModelManager()
print 'testing'

if not m.runModel(-1):
	print 'model files already exist'
	id = m.matrices.checkIdentity((m.matrices.currentMatrix.matrix))
	m._ModelManager__runModelJob(id)
