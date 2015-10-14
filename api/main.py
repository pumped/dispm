from Controller import Controller
from server import Server
from bottle import static_file, route, run
from logger import *

if __name__ == "__main__":

	#threaded
	try:
		controller = Controller()
		controller.start()

		server = Server()
		server.controller = controller

		server.run()

		#wait for termination
		while 1:
			controller.join(1)
			if not controller.isAlive():
				break

	except (KeyboardInterrupt, SystemExit):
		print 'Error: Cylons are killing users!'
		print 'Waiting for Tasks to stop'

	except Exception as ex:
		logging.exception('Uncaught error')
	finally:
		controller.stop()
