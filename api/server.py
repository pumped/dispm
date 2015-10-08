from bottle import Bottle, static_file, route, run
from logger import *
from Config import Config
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
		self._app.route('/getTimeline',callback=self.getTimeline)
		self._app.route('/status',callback=self.status)
		#self._app.route('/set/<project>',callback=self.setData)
		self._app.route('/save/<speciesID>/<timelineID>',callback=self.saveState)
		#self._app.route('/restore/<project>',callback=self.restore)
		self._app.route('/runModel',callback=self.runModel)

	# /
	def default(self):
	    return static_file('index.html', root='data/web/')

	# /status
	def status(self):
		logs = log.getLiveLog()
		modelStatus = "Not Running"
		stats = json.dumps({"modelStatus":modelStatus,"logs":logs}, sort_keys=True, indent=4, separators=(',', ': '))
		#stats += "Queue: " + self.controller.getStatus() +"\n"
		return stats

	# /set/timeline
	def setTimeline(self, id):
		self.controller.model.setMatrix(id)
		return "Timeline set"

	# /set/<project>
	# def setData(self, project="Demo"):
	#     return "Project changed"

	# /setPU/<project>/<id>/<value>
	def saveState(self, speciesID, timelineID):
		#run model
		runID = self.controller.makeID(speciesID, timelineID)
		self.controller.addJob(runID)

		#save it
		return "{state:'ok',response:'state saved, running model',model:{id:'"+runID+"'}}"

	# /restore/<project>
	def restore(self, project):
		return "Model Reset"


	# /runModel
	def runModel(self):
		self.controller.modelQueue.put("test")
		state = self.controller.getCurrentState()
		return json.dumps(state)

	# /getParents
	def getTimeline(self):
		return static_file('parents.json', Config.initialFiles)

	# @route('/data/<filename>')
	# def server_static(filename):
	#     return static_file(filename, root='Marxan/MarZoneData_unix/output')

	from bottle import error
	@error(404)
	def error404(error):
	    return '{"error" : {"code" : 404, "string" : "Invalid Request"}}'

	def run(self):
		self._app.run(host=self._host, port=self._port, quiet=True)
		pass
		#run(host='0.0.0.0', port=5566, debug=True)
