import re

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

    def __init__(this, localid:localid_t, nativeType:str, content:str, lines:tuple[int,int]):
        this.__localid = localid
        this.__nativeType = nativeType
        this.content = content
        this.lines = lines

    @property
    def localid(this): return this.__localid
    
    def __str__(this) -> str:
        return f"--- !u!{this.__nativeType} &{this.__localid}\n{this.content}"
    
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
