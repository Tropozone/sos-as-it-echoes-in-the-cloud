#LOAD selfgraph and self data
import json
import pathlib


# with open('./data/selfgraph.txt', 'r') as json_file:
#     graph = json.load(json_file)
# with open('./data/selfdata.txt', 'r') as json_file:
#     data = json.load(json_file)

# #CHECK
# print(data["lifetime"])
# print(graph.keys())

# #SAVE them as a json
# with open('./data/selfdata.json', 'w') as fp:
#     json.dump(data, fp, sort_keys=True, indent=4)
# with open('./data/graph.json', 'w') as fp:
#     json.dump(graph, fp, sort_keys=True, indent=4)
# with open('./data/selfbirth.txt', 'r') as json_file:
#     selfbirth = json.load(json_file)
# with open('./data/birthgraph.json', 'w') as fp:
#     json.dump(selfbirth, fp, sort_keys=True, indent=4)

#SAVE FILE IN FOLDER WHERE SHOULD BE
import shutil, os
files = ['birthgraph.json', 'graph.json', 'selfdata.json', 'heard_online.txt', 'heard_human.txt', 'hatchVA.txt', 'wiki.txt']
for f in files:
    shutil.copy('./data/'+f, '/Users/lou/Github/test')


#to copy all files where should be