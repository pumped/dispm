from bottle import static_file, route, run


class Server():
	controller = None

	@route('/')
	def default():
	    return "Welcome to the Dispersal Modelling Web API"

	@route('/status')
	def status():
		stats = "Model: Stopped \n"
		#stats += "Queue: " + self.controller.getStatus() +"\n"
		return stats

	@route('/set/<project>')
	def setData(project="Demo"):
	    return "Marxan Ran"

	@route('/setPU/<project>/<id>/<value>')
	def setPU(project,id,value):
		return "PU Set " + project + " " + id + " " + value
		
	@route('/restore/<project>')
	def restore(project):
		return "Model Reset"

	# @route('/data/<filename>')
	# def server_static(filename):
	#     return static_file(filename, root='Marxan/MarZoneData_unix/output')
	    
	from bottle import error
	@error(404)
	def error404(error):
	    return '{"error" : {"code" : 404, "string" : "Invalid Request"}}'

	def run(self):
		print self.controller
		run(host='0.0.0.0', port=5566, debug=True)
