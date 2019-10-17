from flask import Flask, render_template, request 
import json
import ortools_sol     

app = Flask(__name__, template_folder = 'templates')

@app.route("/")
def home():
	iframe = 'test.html'
	return render_template("user.html", iframe=iframe)

@app.route("/test.html", methods=['GET','POST'])
def map():
	if request.method=='GET':
		return render_template("test.html", custom_width = 100)
	if request.method=='POST':
		coordinates = request.get_json()
		print(coordinates)
		print(coordinates['points'])
		# l = len(coordinates['points'])
		return render_template("test.html", start = coordinates['points'][0], end= coordinates['points'][1], custom_width = 50)

@app.route("/points", methods=['POST'])
def points():
	route_addresses = []
	route_points = request.get_json()
	pairs = route_points['pairs']
	plan_output, total_hours, ordered_lat_long = ortools_sol.getOptimalRoute(route_points['points'], pairs)
	for point in plan_output:
		route_addresses.append(route_points['points'][point])
	return json.dumps({'Route': plan_output, 'Addresses': route_addresses, 'GeoCoordinates': ordered_lat_long})

if __name__ == "__main__":
    app.run(debug=True)