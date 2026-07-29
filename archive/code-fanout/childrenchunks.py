import json 
from semanticchunks import semantic_chunker

with open("parentchunks2.json","r") as f:
    data=json.dumpt(f)

for i in data[:5]:
    print(i)