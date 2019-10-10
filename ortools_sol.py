# Copyright 2010-2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START program]
"""Simple Pickup Delivery Problem (PDP)."""

# [START import]
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import data_getter
# [END import]

points = {
    '0': '-122.128646,37.429086',
    '1': '-122.136608,37.454435',
    '2': '-122.162742,37.444651', 
    '3': '-122.136662,37.440990',
    '4': '-122.120184,37.399082',
    '5': '-122.134653,37.414577',
    '6': '-122.134800,37.438400',
    '7': '-122.150500,37.445900',
    '8': '-122.156700,37.436600',
    '9': '-122.133400,37.402500',
    '10': '-122.126400,37.403200'
}

# points = {
#     '0': '80.228786,12.833183',
#     '1': '80.227786,12.901150',
#     '2': '80.222571,12.849674',
#     '3': '80.261448,12.981419',
#     '4': '80.257432,12.963277'
# }

# [START data_model]
def create_data_model():
    """Stores the data for the problem."""
    data = {}

    duration_matrix = ['Too Many Requests']

    while 'Too Many Requests' in duration_matrix:
        duration_matrix[0] = data_getter.GetDurationMatrix(points)

    data['duration_matrix'] = duration_matrix[0]
    
    # [START pickups_deliveries]
    data['pickups_deliveries'] = [
        [1, 2],
        [3, 4],
        [5, 6],
        [7, 8],
        [9, 10]
    ]
    # [END pickups_deliveries]
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data
    # [END data_model]


# [START solution_printer]
def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    total_duration = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_duration = 0
        while not routing.IsEnd(index):
            print(assignment.Value(routing.NextVar(index)))
            if assignment.Value(routing.NextVar(index)) != 0: 
                plan_output += ' {} -> '.format(manager.IndexToNode(index))
            else:
                plan_output += ' {} '.format(manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_duration += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        # plan_output += '{}\n'.format(manager.IndexToNode(index))
        print(plan_output)
        total_duration += route_duration
    total_hours = total_duration/3600
    print('Total Duration of all routes: {} hrs'.format(total_hours))
    # [END solution_printer]


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    # [START data]
    data = create_data_model()
    # [END data]

    # Create the routing index manager.
    # [START index_manager]
    manager = pywrapcp.RoutingIndexManager(
        len(data['duration_matrix']), data['num_vehicles'], data['depot'])

    # [END index_manager]

    # Create Routing Model.
    # [START routing_model]
    routing = pywrapcp.RoutingModel(manager)

    # [END routing_model]

    # Define cost of each arc.
    # [START arc_cost]
    def duration_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['duration_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    # [END arc_cost]

    # Add Distance constraint.
    # [START distance_constraint]
    dimension_name = 'Duration'
    routing.AddDimension(
        transit_callback_index,
        slack_max = 0,  # no slack
        capacity = 10800,  # vehicle maximum travel duration
        fix_start_cumul_to_zero = True,  # start cumul to zero
        name = dimension_name)
    duration_dimension = routing.GetDimensionOrDie(dimension_name)
    duration_dimension.SetGlobalSpanCostCoefficient(100)
    # [END distance_constraint]

    # Define Transportation Requests.
    # [START pickup_delivery_constraint]
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            duration_dimension.CumulVar(pickup_index) <=
            duration_dimension.CumulVar(delivery_index))
    # [END pickup_delivery_constraint]

    # Setting first solution heuristic.
    # [START parameters]
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    # [END parameters]

    # Solve the problem.
    # [START solve]
    assignment = routing.SolveWithParameters(search_parameters)
    # [END solve]

    # Print solution on console.
    # [START print_solution]
    if assignment:
        print_solution(data, manager, routing, assignment)
    # [END print_solution]


if __name__ == '__main__':
    main()
# [END program]