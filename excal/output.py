import sys
import json
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

    def printJson(self):
        out = json.loads('{"issues":[]}')
        for o in self.exeptions:
            a = o.__dict__
            a["start_location"] = o.start_location.__dict__
            a["end_location"] = o.end_location.__dict__
            a["severity"] = o.severity.name
            a["type"] = o.type.name
            out["issues"].append(a)

        print(json.dumps(out, indent=2))

    def printSonarqube(self):
        out = json.loads('{"issues":[]}')
        for o in self.exeptions:
            a = {
                "engineId": "EXCAL",
                "ruleId": o.id,
                "severity": "INFO" if o.severity.name == "CONVENTION" else o.severity.name,
                "type": "CODE_SMELL" if o.type.name == "CONVENTION" else o.type.name,
            }
            a["primaryLocation"] = {
                "message": o.message,
                "filePath": o.file
            }
            a["primaryLocation"]["textRange"] = {
                "startLine": o.start_location.line,
                "endLine": o.end_location.line,
                "startColumn": o.start_location.col,
                "endColumn": o.end_location.col
            }

            out["issues"].append(a)
        print(json.dumps(out, indent=2))
