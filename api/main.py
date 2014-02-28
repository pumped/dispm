from Controller import Controller
from server import Server
from bottle import static_file, route, run

#threaded
try:
	controller = Controller()
	controller.start()

	server = Server()
	server.controller = controller

	server.run()

finally:
	print 'Aborted: Unicorns are killing users!'
	print 'Waiting for Tasks to stop'
	controller.quit = True
