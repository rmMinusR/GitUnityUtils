import re
from typing import *
import yaml

localid_t = int


class UnityObject:
    @staticmethod
    def parse(block:str, lines:tuple[int,int]) -> "UnityObject":
        header = block[0:block.find("\n")]
        matches = re.match(r"--- !u!(\d+) &(-?\d+)", header)
        assert matches != None, f"Expected a header, but got {header}"
        return UnityObject(
            int(matches.group(2)),
            int(matches.group(1)),
            block[block.find("\n")+1:],
            lines
        )

    def __init__(this, localid:localid_t, nativeType:str, rawContent:str, lines:tuple[int,int]):
        this.__localid = localid
        this.__nativeType = nativeType
        this.raw = rawContent
        this.content:dict = yaml.safe_load(this.raw)
        this.lines = lines

    @property
    def localid(this): return this.__localid
    
    def __str__(this) -> str:
        return f"--- !u!{this.__nativeType} &{this.__localid}\n{this.raw}"
    

class UnityFile:
    @staticmethod
    def fromPath(path: str):
        # Read data blocks
        with open(path, "r") as sourceFile:
            lines = sourceFile.readlines()
            lines = [(i[:-1] if i.endswith("\n") else i) for i in lines] # Remove trailing newlines
        return UnityFile(lines)

    @staticmethod
    def fromText(content: str):
        return UnityFile(content.split("\n"))

    def __init__(this, lines):
        this.objects:dict[localid_t, UnityObject] = dict()
        this.header:str = None
        
        # Split into objects
        indices = [i for i in range(len(lines)) if lines[i].startswith("--- !u!")] + [len(lines)]
        this.header = "\n".join(lines[0:indices[0]])
        for i in range(len(indices)-1):
            objContent = "\n".join(lines[ indices[i] : indices[i+1] ])
            obj = UnityObject.parse(objContent, lines)
            this.objects[obj.localid] = obj
    
        assert len(this.objects) > 0, "File was empty!"


class ObjectDiff:
    @staticmethod
    def fromUnityObjects(a:UnityObject, b:UnityObject):
        assert a.localid == b.localid, f"Wrong objects compared: {a.localid} vs {b.localid}"
        assert next(a.content.keys()) == next(b.content.keys()), f"Type of object changed: {next(a.content.keys())} -> {next(b.content.keys())}"
        return ObjectDiff(a.content, b.content)

    def __init__(this, a:dict[str,Any], b:dict[str,Any]):
        this.removed:dict[str,Any] = dict()
        for k in set.difference(a.keys(), b.keys()):
            this.removed[k] = a[k]
                
        this.added:dict[str,Any] = dict()
        for k in set.difference(b.keys(), a.keys()):
            this.added[k] = b[k]
                
        this.modified:dict[str,ObjectDiff|tuple[Any,Any]] = dict()
        for k in set.intersection(a.keys(), b.keys()):
            assert type(a[k]) == type(b[k]), f"Field serialization spec changed: {type(a[k])} -> {type(b[k])}"
            if isinstance(a[k], dict): this.modified[k] = ObjectDiff(a[k], b[k])
            else: this.modified[k] = (a[k], b[k])
