from dataclasses import dataclass
from enum import Enum
from excal.astNode import Location

class OffenceType(Enum):
    CONVENTION = 0
    CODE_SMELL = 1
    VULNERABILITY = 2
    BUG = 3

class Severity(Enum):
    CONVENTION = 0
    INFO = 1
    MINOR = 2
    MAJOR = 3
    CRITICAL = 4
    BLOCKER = 5


@dataclass
class Offence():
    file: str
    start_location: Location
    message: str
    id: str
    end_location: Location = Location(0, 0)
    severity: Severity = Severity.CONVENTION
    type: OffenceType = OffenceType.CONVENTION
