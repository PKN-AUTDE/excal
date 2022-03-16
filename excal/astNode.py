from typing import List
from dataclasses import dataclass
from clang.cindex import CursorKind

@dataclass
class Location():
    filename: str
    line: int
    col: int


class AstNode():
    """Basic data structure containing AST information."""
    def __init__(self, kind: CursorKind, filename: str, line: int, col: int,
                 value: str, indet_level: int, val_type: str, parent: "AstNode") -> None:
        self.kind: CursorKind = kind
        self.location: Location = Location(filename, line, col)
        self.value: str = value
        self.parent: "AstNode" = parent
        self.children: "List[AstNode]" = []
        self.indent_level: int = indet_level
        self.type: str = val_type

    def add_child(self, child: "AstNode") -> None:
        self.children.append(child)

    def __str__(self):
        out = "  " * self.indent_level
        out += str(self.location.line) + ":" + str(self.location.col) + "  " + \
            str(self.kind) + " " + self.value + ": " + self.type
        return out

    def get_older_Siblings(self) -> List["AstNode"]:
        if self.parent is None:
            return []
        return self.parent.children[:self.parent.children.index(self)]

    def get_younger_Siblings(self) -> List["AstNode"]:
        if self.parent is None:
            return []
        return self.parent.children[self.parent.children.index(self):]
