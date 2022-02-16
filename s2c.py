import sys,re, json, urllib.request
from types import SimpleNamespace

#  TODO 
#  - find duplicate {} variables , change and map them differently {client_nr} for removing clients for example

# Connection template 
ConnTemplate = {"data":{"conn":{"general_attributes":{"type":"CONN","name":"","description":"","minimum_ae_version":"11.2"},"connection_attributes":{"platform":"CIT","job_type":"WEBSERVICEREST","sub_type":"RESTCONNECTION"},"documentation":[{"Docu":[""]}],"extended_values":[{"name":"webserviceEndpoint","type":"4","value":"&basePath#"}]}},"path":"CONN"}

## Functions 

def LoadJsonData(Link):
    f = urllib.request.urlopen(Link)
 
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    f.close()

    return data

# Find all variables and map them to Automic varas
def GetVariables(endPoints):
    Variables = dict()

    regex = r"\{(.*?)\}"

    for endPoint in endPoints:
        matches = re.finditer(regex, endPoint, re.DOTALL)

        for matchNum, match in enumerate(matches):
            for groupNum in range(0, len(match.groups())):
                k = "{" + match.group(1) + "}"
                v = "&" + match.group(1) + "#"
                Variables[k] = v

    return Variables

def ReplaceVariables(endPoints, Variables):
    for endPoint in endPoints:
        for k, v in Variables.items():
            endPoint = endPoint.replace(k,v) 
        #print(endPoint)
        yield endPoint

# Logic 

if len(sys.argv) < 2:
    print("Usage: s2c.py url object_name [path] ") 
    sys.exit()
data = LoadJsonData(sys.argv[1])
name = sys.argv[2]


# Read the important bits
title=data['info']['title']
endPoints=data['paths']

Variables = GetVariables(endPoints)

ConnTemplate['data']['conn']['general_attributes']['description'] = title
ConnTemplate['data']['conn']['general_attributes']['name'] = name
if len(sys.argv)  > 3 :
    ConnTemplate['path'] = sys.argv[3]
    


class Res:
    name = ""
    type = "4"
    value = ""

c = 0
for i in ReplaceVariables(endPoints,Variables):
# Ther are always two entries 0 and 1 
    for a in range(2):
        r = Res()
        r.name = "resources_{}_{}".format(c,a)
        r.type = "4"
        r.value = i
        ConnTemplate['data']['conn']['extended_values'].append(r)
# Increment the resources counter
    c +=  1

if len(Variables) > 0:
    ConnTemplate['data']['conn']['documentation'][0]['Docu'][0] = "Following variables have been replaced:"
    for k, v in Variables.items():
        ConnTemplate['data']['conn']['documentation'][0]['Docu'].append(k + " = " + v )

print(json.dumps(ConnTemplate, default=lambda o: o.__dict__, sort_keys=False, indent=4))
