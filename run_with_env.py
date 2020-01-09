import os
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from util import env_vars

def main():
    os.environ.update(env_vars())
    os.execvp(sys.argv[1], sys.argv[1:])

if __name__ == '__main__':
    main()
