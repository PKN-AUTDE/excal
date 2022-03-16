import sys
from typing import List
from typing import Tuple


class Output():
    """Output class. Will be extended by more output options."""
    def __init__(self):
        self.exeptions: List[Tuple[str, int, int, str]] = []
        return

    def addExeptioins(self, ex: List[Tuple[str, int, int, str]]):
        self.exeptions.extend(ex)

    def printError(self):
        for e in self.exeptions:
            print(f'{e[0]}: {e[1]}:{e[2]} : {e[3]}', file=sys.stderr)
