from pathlib import Path
from typing import List
from clang.cindex import Index as CIndex, Cursor, TranslationUnit

from excal.astNode import AstNode


class CWalker:
    def __init__(self, c_file: Path, clang_args: List[str]) -> None:
        self.anonymous_counter = 0
        self.path: Path = c_file
        # use clang to parse C file
        self.index: CIndex = CIndex.create()
        self.parsed_unit: TranslationUnit = self.index.parse(c_file, args=clang_args)
        self.root_node: Cursor = self.parsed_unit.cursor
        self.ast: AstNode

    def walkRec(self, node: Cursor, indent: str, ast: AstNode) -> None:
        indent += '  '
        for child_node in node.get_children():
            try:
                if not self.path.samefile(child_node.location.file.name):
                    continue
            except Exception:
                continue
            ast_child = AstNode(child_node.kind, child_node.location.file.name,
                                child_node.location.line, child_node.location.column,
                                str(child_node.spelling), ast.indent_level + 1,
                                str(child_node.type.spelling), ast)
            ast.add_child(ast_child)
            self.walkRec(child_node, indent, ast_child)

    def walk(self) -> AstNode:
        self.ast = AstNode(self.root_node.kind, "", 0, 0,
                           str(self.root_node.spelling), 0, "", None)
        self.walkRec(self.root_node, '', self.ast)
        return self.ast
