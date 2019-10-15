from flask import Flask, render_template, request 
import json
import ortools_sol     

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    iframe = 'test.html'
    return render_template("user.html", iframe=iframe)

@app.route("/test.html")
def map():
	data = {'A':[80.257432,12.963277], 'B':[80.261448,12.981419]}
	return render_template("test.html", data = data)

@app.route("/points", methods=['GET','POST'])
def points():
	route_addresses = []
	route_points = request.get_json()
	pairs = route_points['pairs']
	curr_loc = [float(x) for x in route_points['points'][0].split(',')]
	plan_output, total_hours = ortools_sol.getOptimalRoute(route_points['points'], pairs)
	for point in plan_output:
		route_addresses.append(route_points['points'][point])
	return json.dumps({'Route': plan_output, 'Addresses': route_addresses})

if __name__ == "__main__":
    app.run(debug=True)