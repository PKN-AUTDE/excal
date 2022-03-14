from pathlib import Path
from typing import List

from astNode import AstNode
from cwalker import CWalker
from visitor import CXXAstNodeVisitor
from pluginManager import PluginManager
from output import Output


class Analyzer:
    def __init__(self, include_dirs: List[str], clang_args: List[str], pm: PluginManager, out: Output) -> None:
        self.include_dirs: List[Path] = [Path(p) for p in include_dirs]
        # Check for additional includes in args
        arg_includes = [arg[2:] for arg in clang_args if arg.startswith("-I")]
        self.include_dirs.extend([Path(inc) for inc in arg_includes if inc not in include_dirs])
        # And store only non includes
        self.additional_arguments = [arg for arg in clang_args if not arg.startswith("-I")]
        self.ast: AstNode
        self.pm: PluginManager = pm
        self.out: Output = out

    def find_file(self, file_name: str) -> Path:
        result = Path(file_name)
        if result.exists():
            return result
        for inc_dir in self.include_dirs:
            result = inc_dir / file_name
            if result.exists():
                return result
        return None

    def clang_args(self) -> List[str]:
        result = self.additional_arguments.copy()
        result.extend([f"-I{inc}" for inc in self.include_dirs])
        return result

    def printAstRec(self, node: AstNode):
        print(node)
        for child in node.children:
            self.printAstRec(child)

    def analyze(self, file_name: str, printAst: bool) -> None:
        in_path = self.find_file(file_name)
        print(f"Parsing {file_name}")
        walker = CWalker(in_path, self.clang_args())
        self.ast = walker.walk()

        visitor = CXXAstNodeVisitor(self.ast, self.pm)
        visitor.visit()
        self.out.addExeptioins(visitor.getExceptions())

        if printAst:
            self.printAstRec(self.ast)
