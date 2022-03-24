import sys
from typing import List
from excal.offence import Offence


class Output():
    """Output class. Will be extended by more output options."""
    def __init__(self):
        self.exeptions: List[Offence] = []
        return

    def addExeptioins(self, ex: List[Offence]):
        self.exeptions.extend(ex)

    def printError(self):
        for e in self.exeptions:
            print(f'{e.file}: {e.start_location.line}:{e.start_location.col} : {e.id} {e.message}', file=sys.stderr)

