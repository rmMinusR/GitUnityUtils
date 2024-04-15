import argparse
parser = argparse.ArgumentParser(
    prog="Split asset (Version Control Helpers for Unity)",
    description="Splits a Unity file into multiple files, one for each object. Useful for complex merges/diffs."
)
parser.add_argument("input")
parser.add_argument("output", nargs="?")


import time
import sys, os, shutil
from unityfile import *

start = time.perf_counter()

args = parser.parse_args()
assetFile = UnityFile.fromPath(args.input)

# Setup destination
if args.output == None: args.output = args.input+".split"
if os.path.exists(args.output):
    assert os.path.isdir(args.output), f"Expected a directory, but {parser.output} was a file"
    shutil.rmtree(args.output)
os.mkdir(args.output)

# Write split data
for k in assetFile.objects.keys():
    objFilePath = os.path.join(args.output, str(k)+".yml")
    with open(objFilePath, "w+") as objectFile:
        objectFile.write(assetFile.header+"\n"+str(assetFile.objects[k])+"\n")

end = time.perf_counter()
print(f"Extracted {len(assetFile.objects)} objects in {end-start}s")
