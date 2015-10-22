from Controller import Controller
from server import *
from bottle import static_file, route, run
from logger import *
import time

if __name__ == "__main__":

	#threaded
	try:
		controller = Controller()
		controller.daemon = True
		controller.start()

		ws = webServer()
		ws.runWebServer(controller)
		controller.onMessage(ws.emit)

		#wait for termination
		while threading.active_count() > 0:
			time.sleep(0.1)

	except (KeyboardInterrupt, SystemExit):
		print 'Error: Cylons are killing users!'
		print 'Waiting for Tasks to stop'

	# except Exception as ex:
	# 	print ex
	finally:
		controller.stop()
