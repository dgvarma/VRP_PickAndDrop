from flask import Flask, render_template, request 
import json     

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("user.html")

@app.route("/points", methods=['POST'])
def points():
	route_points = request.get_json()
	print(route_points)
	return 'OK'


if __name__ == "__main__":
    app.run(debug=True)