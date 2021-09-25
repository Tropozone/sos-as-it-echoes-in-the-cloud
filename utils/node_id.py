import json

node001={
    "name": "miakk",
    "id": 1,
    "location": "Eindhoven",
    "country": "Belgium",
    "continent": "Europe",

}

with open("node001.json", "w+") as outfile:
    json.dump(node001, outfile)
node002={
    "name": "öggiu",
    "id": 2,
    "location": "Copenhagen",
    "country": "Denmark",
    "continent": "Europe",

}

with open("node002.json", "w+") as outfile:
    json.dump(node002, outfile)

node003={
    "name": "ökbac",
    "id": 3,
    "location": "Bruxelles",
    "country": "Belgium",
    "continent": "Europe",

}


with open("node003.json", "w+") as outfile:
    json.dump(node003, outfile)


bug={
    "name": "eabü",
    "id": 666,
    "location": "internet",
    "country": "internet",
    "continent": "internet"

}


with open("bug.json", "w+") as outfile:
    json.dump(bug, outfile)