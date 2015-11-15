from tornado import websocket, web, ioloop
import json
import time
import sys, traceback
from threading import Thread
import StringIO

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
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "accept, cache-control, origin, x-requested-with, x-file-name, content-type")

	@web.asynchronous
	def get(self, *args):

		try:
			r = self.get_argument("r",default=None)
			print r

			if (r == "runModel"):
				speciesID = self.get_argument("species",default=None)
				timelineID = self.get_argument("timeline",default=None)
				prevention = self.get_argument("prevention",default=None)
				protection = self.get_argument("protection",default=None)
				if speciesID and timelineID:
					self.controller.addJob(speciesID, timelineID, prevention, protection)
					self.write('{"status":"OK"}')
				else:
					self.write("error, missing paramaters")

			elif (r == "getStatus"):
				pass

			elif (r == "getTimeline"):
				speciesID = self.get_argument("species",default=None)
				if speciesID:
					timeline = self.controller.getTimeline(speciesID)
					if timeline:
						self.write(timeline)
					else:
						self.write("")

			# value = self.get_argument("value")
			# data = {"id": id, "value" : value}
			# data = json.dumps(data)
			# for c in cl:
			# 	c.write_message(data)

			self.finish()
		except:
			print "Unexpected error:", sys.exc_info()[0]

	@web.asynchronous
	def post(self):
		pass


class WMSHandler(web.RequestHandler):
	def set_default_headers(self):
		self.set_header("Access-Control-Allow-Origin", "*")
		self.set_header("Access-Control-Allow-Headers", "accept, cache-control, origin, x-requested-with, x-file-name, content-type")
		self.set_header("Content-type", "image/png")

	@web.asynchronous
	def get(self, *args):

		try:
			params = {}
			params['bbox'] = self.get_argument("BBOX",default=None)
			params['width'] = self.get_argument("WIDTH",default=None)
			params['height'] = self.get_argument("HEIGHT",default=None)
			params['time'] = self.get_argument("time",default=None)
			params['species'] = self.get_argument("species",default=None)
			params['timeline'] = self.get_argument("timeline",default=None)

			if params['bbox'] and params['width'] and params['height'] and params['time'] and params['species'] and params['timeline']:
				output = self.wms.getMap(params)
				if output:

					self.write(output)
				else:
					self.write("failed")

			else:
				self.write("invalid request")

		except:
			print "Unexpected error:", sys.exc_info()[0]
			traceback.print_exc(file=sys.stdout)
		finally:
			self.finish()


class webServer:

	def emit(self,data):
		#print data
		for c in cl:
			c.write_message(data)

	def runWebServer(self,cntrl,wms):
		ApiHandler.controller = cntrl
		SocketHandler.controller = cntrl
		WMSHandler.wms = wms

		app = web.Application([
			(r'/ws', SocketHandler),
			(r'/api', ApiHandler),
			(r'/wms', WMSHandler),
			(r'/(.*)', web.StaticFileHandler, {'path': "data/web", "default_filename": "index.html"})
		],
		debug=True)

		app.listen(5566)

		self.t = Thread(target=ioloop.IOLoop.instance().start)
		self.t.daemon = True
		self.t.start()

	def stop():
		self.t.stop()
