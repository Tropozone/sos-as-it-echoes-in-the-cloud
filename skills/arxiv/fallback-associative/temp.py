import pathlib
import json

print("Hatching self in process...")
memory=["technology", "mycroft", "AI"]
self_data = dict.fromkeys(["lifetime", "memory"])
self_data["lifetime"],self_data["memory"]=26, memory

with open(str(pathlib.Path(__file__).parent.absolute())+'/data/selfdata.txt', 'w') as outfile:
    json.dump(self_data, outfile)
    print("added memory field")