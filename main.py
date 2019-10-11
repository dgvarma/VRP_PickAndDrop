from flask import Flask, render_template, request 
import json
import ortools_sol     

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("user.html")

@app.route("/points", methods=['POST'])
def points():
	route_points = request.get_json()
	pairs = route_points['pairs']
	plan_output, total_hours = ortools_sol.getOptimalRoute(route_points['points'], pairs)
	print(plan_output)
	print(total_hours)
	return 'OK'


if __name__ == "__main__":
    app.run(debug=True)