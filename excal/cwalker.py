from pathlib import Path
from typing import List
from clang.cindex import Index as CIndex, Cursor, TranslationUnit
import os
import hashlib
import pickle

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
        self.baseDir = baseDir
        self.parsed_unit: TranslationUnit = None
        self.root_node: Cursor = None

        if self.use_cache:
            self.excalDir = self.baseDir / ".excal"
            if not os.path.isdir(self.excalDir):
                os.mkdir(self.excalDir)
            file = open(self.path)
            fileC = file.read()
            hash = hashlib.sha256(fileC.encode())
            file.close()
            self.hash = hash.hexdigest()

            if not os.path.isfile(self.excalDir / self.hash):
                self.parsed_unit = self.index.parse(self.path, args=self.args)
                self.root_node = self.parsed_unit.cursor
                # TL.save(self.excalDir / hash.hexdigest())
        else:
            self.parsed_unit = self.index.parse(self.path, args=self.args)
            self.root_node = self.parsed_unit.cursor

        self.ast: AstNode

    def walkRec(self, node: Cursor, indent: str, ast: AstNode) -> None:
        indent += '  '
        for child_node in node.get_children():
            try:
                if not self.path.samefile(child_node.location.file.name):
                    continue
            except Exception:
                continue
            ast_child = AstNode(str(child_node.kind), child_node.location.file.name,
                                child_node.location.line, child_node.location.column,
                                child_node.extent.end.line, child_node.extent.end.column,
                                str(child_node.spelling), ast.indent_level + 1,
                                str(child_node.type.spelling), ast,
                                [Token(str(x.kind), x.spelling, Location(x.location.line, x.location.column)) for x in child_node.get_tokens()])

            ast.add_child(ast_child)
            self.walkRec(child_node, indent, ast_child)

    def walk(self) -> AstNode:
        self.excalDir = self.baseDir / ".excal"

        if self.use_cache and os.path.isfile(self.excalDir / self.hash):
            cFile = open(self.excalDir / self.hash, "rb")
            self.ast = pickle.load(cFile)
        else:
            self.ast = AstNode(str(self.root_node.kind), "", 0, 0, self.root_node.extent.end.line, self.root_node.extent.end.column, str(self.root_node.spelling), 0, "", None, [Token(str(x.kind), x.spelling, Location(x.location.line, x.location.column)) for x in self.root_node.get_tokens()])
            self.walkRec(self.root_node, '', self.ast)

        if self.use_cache and not os.path.isfile(self.excalDir / self.hash):
            with open(self.excalDir / self.hash, 'wb') as fh:
                pickle.dump(self.ast, fh)
        return self.ast
