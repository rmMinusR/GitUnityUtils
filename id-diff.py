import argparse
from fileinput import filename
parser = argparse.ArgumentParser(
    prog="Diff by ID (Version Control Helpers for Unity)",
    description="Diffs 1) objects that were added/removed and 2) content within an object that was added/removed."
)
subparsers = parser.add_subparsers(dest="subparser_name")

parser_mode_twoFiles = subparsers.add_parser("file", description="Compare two different files currently on disk")
parser_mode_twoFiles.add_argument("fileA")
parser_mode_twoFiles.add_argument("fileB")

parser_mode_history  = subparsers.add_parser("history", description="Compare a file with a previous revision")
parser_mode_history.add_argument("file")
parser_mode_history.add_argument("-git", nargs="?", default="git", help="Use explicit Git executable. May be necessary if no git exists on PATH.")
parser_mode_history.add_argument("copyA")
parser_mode_history.add_argument("copyB", nargs="?", help="If blank, uses copy currently on disk")


args = parser.parse_args()


import time
import sys, os, shutil
from unityfile import *

start = time.perf_counter()

# Load file content
fileA = None
fileB = None
if args.subparser_name == "file":
    # Two-files mode

    if not os.path.isfile(args.fileA):
        print(f"{args.fileA} not found. Exiting...")
        sys.exit(1)

    if not os.path.isfile(args.fileB):
        print(f"{args.fileB} not found. Exiting...")
        sys.exit(1)
        
    fileA = UnityFile.fromPath(args.fileA)
    fileB = UnityFile.fromPath(args.fileB)

elif args.subparser_name == "history":
    # Previous revision mode

    if not os.path.isfile(args.file):
        print(f"{args.file} not found. Exiting...")
        sys.exit(1)

    # Ensure Git works
    import subprocess
    try: subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Git not found. Exiting...")
        sys.exit(1)

    # Load file content
    def retrieveFileContent(path:str, commit:str) -> str|None:
        dirName = os.path.dirname(path)
        fileName = args.file[len(dirName)+1:]
        proc = subprocess.run(
            ["git", "show", f"{commit}:{fileName}"],
            cwd=dirName,
            capture_output=True,
            text=True
        )
        proc.check_returncode()
        return proc.stdout

    fileA = UnityFile.fromText(retrieveFileContent(args.file, args.copyA))
    if args.copyB != None: fileB = UnityFile.fromText(retrieveFileContent(args.file, args.copyB))
    else:                  fileB = UnityFile.fromPath(args.file)
else: assert False

# Diff
print(f"--- a/{args.file}")
print(f"+++ b/{args.file}")
diff = ObjectDiff(fileA, fileB)
print(str( diff ))

end = time.perf_counter()
