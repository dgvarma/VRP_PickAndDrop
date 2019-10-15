from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import data_getter

def create_data_model(points, pairs):
    data = {}

    duration_matrix = ['Too Many Requests']

    while 'Too Many Requests' in duration_matrix:
        duration_matrix[0] = data_getter.GetDurationMatrix(points)

    #removing the depot from the points

    duration_matrix[0][0] = [0] * len(duration_matrix[0][0])

    for row in duration_matrix[0]:
        row[0] = 0

    data['duration_matrix'] = duration_matrix[0]
    
    data['pickups_deliveries'] = pairs

    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, assignment):
    total_duration = 0
    route = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_duration = 0
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_duration += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        total_duration += route_duration
    total_hours = total_duration/3600
    print('Total Duration of all routes: {} hrs'.format(total_hours))
    print('Route: ', route[1:])
    return route[1:], total_hours


def getOptimalRoute(points, pairs):

    lat_long_points= data_getter.getLatLong(points)

    data = create_data_model(lat_long_points, pairs)

    print(lat_long_points)

    print(data)

    manager = pywrapcp.RoutingIndexManager(
        len(data['duration_matrix']), data['num_vehicles'], data['depot'])

    routing = pywrapcp.RoutingModel(manager)

    def duration_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['duration_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(duration_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    dimension_name = 'Duration'
    routing.AddDimension(
        transit_callback_index,
        slack_max = 0,  # no slack
        capacity = 10800,  # vehicle maximum travel duration
        fix_start_cumul_to_zero = True,  # start cumul to zero
        name = dimension_name)
    duration_dimension = routing.GetDimensionOrDie(dimension_name)
    duration_dimension.SetGlobalSpanCostCoefficient(100)

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

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

    assignment = routing.SolveWithParameters(search_parameters)
 
    if assignment:
        plan_output, total_hours = print_solution(data, manager, routing, assignment)
        return plan_output, total_hours
