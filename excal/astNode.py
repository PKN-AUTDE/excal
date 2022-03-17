from typing import List
from dataclasses import dataclass
from clang.cindex import CursorKind, TokenKind


@dataclass
class Location():
    line: int
    col: int


@dataclass
class Token():
    kind: TokenKind
    value: str
    location_start: Location
    # location_end: Location


class AstNode():
    """Basic data structure containing AST information."""
    def __init__(self, kind: CursorKind, filename: str, line: int, col: int, end_line: int,
                 end_col: int, value: str, indet_level: int, val_type: str,
                 parent: "AstNode", tokens: List["Token"]) -> None:
        self.kind: CursorKind = kind
        self.location: Location = Location(line, col)
        self.filename = filename
        self.end_location: Location = Location(end_line, end_col)
        self.value: str = value
        self.parent: "AstNode" = parent
        self.children: List["AstNode"] = []
        self.indent_level: int = indet_level
        self.type: str = val_type
        self.tokens: List["Token"] = tokens

    def add_child(self, child: "AstNode") -> None:
        self.children.append(child)

    def __str__(self):
        out = "  " * self.indent_level
        out += str(self.location.line) + ":" + str(self.location.col) + "-" + \
            str(self.end_location.line) + ":" + str(self.end_location.col) + "  " + \
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

    def printTokens(self):
        for t in self.tokens:
            print("  " * self.indent_level + "|" + t.value.replace("\n", "\n|") + f" :{t.kind} {t.location_start.line}:{t.location_start.col}")
