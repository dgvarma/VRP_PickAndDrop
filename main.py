from flask import Flask, render_template, request 
import json
import ortools_sol     

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("user.html")

@app.route("/points", methods=['GET','POST'])
def points():
	route_points = request.get_json()
	pairs = route_points['pairs']
	curr_loc = [float(x) for x in route_points['points'][0].split(',')]
	plan_output, total_hours = ortools_sol.getOptimalRoute(route_points['points'], pairs)
	# return render_template("test.html")
	# return 'OK'
	return json.dumps({})

if __name__ == "__main__":
    app.run(debug=True)