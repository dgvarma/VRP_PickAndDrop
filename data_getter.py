import subprocess
from ast import literal_eval
import geocoder

API_KEY = 'ZK1d9qSLfuvvYsWP2OrARqBGxd0Z7mKM'

def getURL(points):
    url = 'http://router.project-osrm.org/table/v1/driving/'
    for i in range(len(points)):
        if i!=len(points)-1:
            url += points[str(i)]+';'
        else:
            url += points[str(i)]
    return url


def GetDurationMatrix(points):
    url = getURL(points)
    cmd = ['curl', url]
    out = subprocess.Popen(cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding='utf-8')
    o, e = out.communicate()
    output = o[o.find('{'):].replace('\n','')
    d = literal_eval(output)
    if 'durations' in d:
        return d['durations']
    else:
        return d['message']

def getLatLong(lat_long_points):
    points = {}
    points[str(0)] = lat_long_points[0]
    addresses = lat_long_points[1:]
    for i in range(len(addresses)):
        g = geocoder.mapquest(addresses[i], key = API_KEY)
        coordinates_string = str(g.lng)+','+str(g.lat)
        points[str(i+1)] = coordinates_string
    return points

