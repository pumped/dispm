from bottle import Bottle, static_file, route, run
from logger import *
import json


class Server():
	controller = None

	def __init__(self, host='0.0.0.0', port=5566):
		self._host = host
		self._port = port
		self._app = Bottle()
		self._route()

	def _route(self):
		self._app.route('/',callback=self.default)
		self._app.route('/status',callback=self.status)
		self._app.route('/set/<project>',callback=self.setData)
		self._app.route('/setPU/<project>/<id>/<value>',callback=self.setPU)
		self._app.route('/restore/<project>',callback=self.restore)
		self._app.route('/runModel',callback=self.runModel)

	# /
	def default(self):
	    return static_file('index.html', root='data/web/')

	# /status
	def status(self,):
		logs = log.getLiveLog()
		modelStatus = "Not Running"
		stats = json.dumps({"modelStatus":modelStatus,"logs":logs}, sort_keys=True, indent=4, separators=(',', ': '))
		#stats += "Queue: " + self.controller.getStatus() +"\n"
		return stats

	# /set/<project>
	def setData(self, project="Demo"):
	    return "Project changed"

	# /setPU/<project>/<id>/<value>
	def setPU(self, project, id, value):
		return "PU Set " + project + " " + id + " " + value
		
	# /restore/<project>
	def restore(self, project):
		return "Model Reset"

	# /runModel
	def runModel(self):
		self.controller.modelQueue.put("test")
		return "Modeller Started"

	# @route('/data/<filename>')
	# def server_static(filename):
	#     return static_file(filename, root='Marxan/MarZoneData_unix/output')
	    
	from bottle import error
	@error(404)
	def error404(error):
	    return '{"error" : {"code" : 404, "string" : "Invalid Request"}}'

	def run(self):
		self._app.run(host=self._host, port=self._port)
		pass
		#run(host='0.0.0.0', port=5566, debug=True)