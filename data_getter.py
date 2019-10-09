import subprocess
from ast import literal_eval

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
