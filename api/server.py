from tornado import websocket, web, ioloop
import json
import time
from threading import Thread

cl = []

class IndexHandler(web.RequestHandler):
	def get(self):
		self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True

	def open(self):
		if self not in cl:
			cl.append(self)

	def on_close(self):
		if self in cl:
			cl.remove(self)

class ApiHandler(web.RequestHandler):

	@web.asynchronous
	def get(self, *args):

		r = self.get_argument("r",default=None)
		print r

		if (r == "runModel"):
			print self.controller
			self.controller.modelQueue.put("test")
			state = self.controller.getCurrentState()
			self.write(json.dumps(state))

		elif (r == "getStatus"):
			pass

		# value = self.get_argument("value")
		# data = {"id": id, "value" : value}
		# data = json.dumps(data)
		# for c in cl:
		# 	c.write_message(data)

		self.finish()

	@web.asynchronous
	def post(self):
		pass

class webServer:

	def emit(self,data):
		print data
		for c in cl:
			c.write_message(data)

	def runWebServer(self,cntrl):
		ApiHandler.controller = cntrl
		SocketHandler.controller = cntrl

		app = web.Application([
			(r'/ws', SocketHandler),
			(r'/api', ApiHandler),
			(r'/(.*)', web.StaticFileHandler, {'path': "data/web", "default_filename": "index.html"})
		])

		app.listen(5566)

		self.t = Thread(target=ioloop.IOLoop.instance().start)
		self.t.daemon = True
		self.t.start()

	def stop():
		self.t.stop()
