import subprocess, re, random
from ast import literal_eval
import geocoder

API_KEY = 'ZK1d9qSLfuvvYsWP2OrARqBGxd0Z7mKM'

def getURL(points):
    url = 'http://router.project-osrm.org/table/v1/driving/'
    for i in range(len(points)):
        point = ','.join(map(str, points[i]))
        if i!=len(points)-1:
            url += point+';'
        else:
            url += point
    return url

def getAPIResponse(url):
    cmd = ['curl', url]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding='utf-8')
    output, error = process.communicate()
    return output

def GetDurationMatrix(points):
    url = getURL(points)
    o = getAPIResponse(url)
    output = o[o.find('{'):].replace('\n','')
    d = literal_eval(output)
    if 'durations' in d:
        return d['durations']
    else:
        return d['message']

def getLatLong(route_points):
    lat_long_points = []
    print("Points received to get lat long: ", route_points)
    if type(route_points)==list:
        for i in range(len(route_points)):
            geo_loc = geocoder.mapquest(route_points[i], key = API_KEY)
            lat_long_points.append([geo_loc.lng, geo_loc.lat])
        return lat_long_points
    if type(route_points)==str:
        geo_loc = geocoder.mapquest(route_points, key = API_KEY)
        lat_long_point = [geo_loc.lng, geo_loc.lat]
        return lat_long_point

def getCurrentLocation(visited_point, to_be_visited_point):
    mid_geo_points = []
    while len(mid_geo_points)==0:
        visited_point_string = ','.join(map(str,visited_point))
        to_be_visited_point_string = ','.join(map(str, to_be_visited_point))
        url = "http://router.project-osrm.org/route/v1/driving/" + visited_point_string + ";" + to_be_visited_point_string + "?steps=true&alternatives=false&overview=full"
        output = getAPIResponse(url)
        pattern = "-?\d+\.+\d+\,+\d+\.+\d+"
        mid_geo_points = re.findall(pattern, output)
    driver_current_location = random.choice(list(set(mid_geo_points)))
    driver_current_location = [float(point) for point in driver_current_location.split(',')]
    return driver_current_location

