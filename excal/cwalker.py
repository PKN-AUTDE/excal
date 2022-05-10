from pathlib import Path
from typing import List
from clang.cindex import Index as CIndex, Cursor, TranslationUnit
import os
import hashlib

from excal.astNode import AstNode, Location, Token


class CWalker:
    """Create AST and translate it to astNodes"""
    def __init__(self, c_file: Path, clang_args: List[str], cache: bool, baseDir: Path) -> None:
        self.anonymous_counter = 0
        self.path: Path = c_file
        self.args = clang_args
        # use clang to parse C file
        self.index: CIndex = CIndex.create()
        self.use_cache = cache
        self.parsed_unit: TranslationUnit = self.getTL(baseDir)
        self.root_node: Cursor = self.parsed_unit.cursor
        self.ast: AstNode

    def getTL(self, baseDir: Path) -> TranslationUnit:
        if self.use_cache:
            excalDir = baseDir / ".excal"
            if not os.path.isdir(excalDir):
                os.mkdir(excalDir)
            file = open(self.path)
            fileC = file.read() + str(self.path)
            hash = hashlib.sha256(fileC.encode())
            file.close()

            if not os.path.isfile(excalDir / hash.hexdigest()):
                TL: TranslationUnit = self.index.parse(self.path, args=self.args)
                TL.save(excalDir / hash.hexdigest())
                return TL
            else:
                return TranslationUnit.from_ast_file(excalDir / hash.hexdigest(), index=self.index)

        return self.index.parse(self.path, args=self.args)

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
                                child_node.extent.end.line, child_node.extent.end.column,
                                str(child_node.spelling), ast.indent_level + 1,
                                str(child_node.type.spelling), ast,
                                [Token(x.kind, x.spelling, Location(x.location.line, x.location.column)) for x in child_node.get_tokens()])

            ast.add_child(ast_child)
            self.walkRec(child_node, indent, ast_child)

    def walk(self) -> AstNode:
        self.ast = AstNode(self.root_node.kind, "", 0, 0, self.root_node.extent.end.line, self.root_node.extent.end.column, str(self.root_node.spelling), 0, "", None, [Token(x.kind, x.spelling, Location(x.location.line, x.location.column)) for x in self.root_node.get_tokens()])
        # for token in self.root_node.get_tokens():
        # print(token.spelling)
        # print(f"{token.location.line}: {token.location.column}: {token.kind}")
        self.walkRec(self.root_node, '', self.ast)
        return self.ast
