import re

localid_t = int


class UnityObject:
    @staticmethod
    def parse(block:str, lines:tuple[int,int]) -> "UnityObject":
        header = block[0:block.find("\n")]
        matches = re.match(r"--- !u!(\d+) &(-?\d+)", header)
        assert matches != None
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
