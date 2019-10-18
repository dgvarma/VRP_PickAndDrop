from flask import Flask, render_template, request 
import json, geocoder, re
import ortools_sol  

app = Flask(__name__, template_folder = 'templates')

driver_initial_location = [-122.128646,37.429086]

visited_addresses = []
non_visited_addresses = []
source_destination_pairs = []
ordered_addresses = []

def getCurrentLocation(last_visited_point, to_be_visited_point):
	driver_current_location = ortools_sol.getCurrentLocation(last_visited_point, to_be_visited_point)
	return driver_current_location

@app.route("/")
def home():
	iframe = 'map.html'
	return render_template("user.html", iframe=iframe)

@app.route("/map.html", methods=['GET','POST'])
def map():
	if request.method=='GET':
		return render_template("map.html", center=driver_initial_location, custom_width = 100)
	if request.method=='POST':
		ordered_coordinates = request.get_json()
		if len(ordered_coordinates)>1:
			start_coordinate = ordered_coordinates[0]
			end_coordinate = ordered_coordinates[1]
		else:
			start_coordinate = ordered_coordinates[0]
			end_coordinate = ordered_coordinates[0]
		return render_template("map.html", center=driver_initial_location, start = start_coordinate, end= end_coordinate, custom_width = 70)

@app.route("/markvisited", methods=['POST'])
def markVisitedAddresses():
	details_marked = request.get_json()
	visited_address = details_marked['marked_address']
	ordered_coordinates = details_marked['ordered_coordinates']
	for pair in source_destination_pairs:
		if non_visited_addresses.index(visited_address) in pair:
			source_destination_pairs.remove(pair)
			break
	driver_current_location = ordered_coordinates[ordered_addresses.index(visited_address)+1]
	del ordered_coordinates[ordered_addresses.index(visited_address)+1]
	non_visited_addresses.remove(visited_address)
	visited_addresses.append(visited_address)
	ordered_addresses.remove(visited_address)
	ordered_coordinates[0] = driver_current_location
	if len(non_visited_addresses)==1:
		visited_addresses.clear()
		source_destination_pairs.clear()
		ordered_addresses.clear()
		return json.dumps({'status':'TripEnded', 'ordered_coordinates': ordered_coordinates})
	else:
		return json.dumps({'status':'AddressVisited', 'ordered_coordinates': ordered_coordinates})

@app.route("/addtoride", methods=['POST'])
def addPointsToRide():
	if len(non_visited_addresses)==0:
		non_visited_addresses.append(driver_initial_location)
	else:
		if len(visited_addresses)==0:
			non_visited_addresses[0] = getCurrentLocation(non_visited_addresses[0], ordered_addresses[0])
		else:
			non_visited_addresses[0] = getCurrentLocation(visited_addresses[-1], ordered_addresses[0])
	ordered_addresses.clear()
	new_points = request.get_json()
	pickup_address = new_points['pickup'].strip()
	drop_address = new_points['drop'].strip()
	if pickup_address not in non_visited_addresses:
		non_visited_addresses.append(pickup_address)
	if drop_address not in non_visited_addresses:
		non_visited_addresses.append(drop_address)
	new_pair = [non_visited_addresses.index(pickup_address), non_visited_addresses.index(drop_address)]
	if new_pair not in source_destination_pairs:
		source_destination_pairs.append(new_pair)
	plan_output, ordered_coordinates = ortools_sol.getOptimalRoute(non_visited_addresses, source_destination_pairs)
	for point in plan_output[1:]:
		ordered_addresses.append(non_visited_addresses[point])
	return json.dumps({'route_addresses': ordered_addresses, 'ordered_coordinates': ordered_coordinates})


if __name__ == "__main__":
    app.run(debug=True)