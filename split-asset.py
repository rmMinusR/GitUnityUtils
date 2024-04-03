import time
import sys, os
from unityfile import *

start = time.perf_counter()

sourceFilePath = sys.argv[1]
objects:dict[localid_t, UnityObject] = dict()
fileHeader:str = None

# Read data blocks
with open(sourceFilePath, "r") as sourceFile:
    lines = sourceFile.readlines()
    lines = [(i[:-1] if i.endswith("\n") else i) for i in lines] # Remove trailing newlines

    # Split into objects
    indices = [i for i in range(len(lines)) if lines[i].startswith("--- !u!")] + [len(lines)]
    fileHeader = "\n".join(lines[0:indices[0]])
    for i in range(len(indices)-1):
        objContent = "\n".join(lines[ indices[i] : indices[i+1] ])
        obj = UnityObject.parse(objContent, lines)
        objects[obj.localid] = obj
    
assert len(objects) > 0, "Nothing to split"

# Write split data
for k in objects.keys():
    splitDir = sourceFilePath+".split/"
    if not os.path.exists(splitDir): os.mkdir(splitDir)
    with open(splitDir+str(k)+".yml", "w+") as objectFile:
        objectFile.write(fileHeader+"\n"+str(objects[k])+"\n")

end = time.perf_counter()
print(f"Extracted {len(objects)} objects in {end-start}s")
