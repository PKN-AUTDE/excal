from pathlib import Path
from typing import List

from excal.astNode import AstNode
from excal.cwalker import CWalker
from excal.visitor import CXXAstNodeVisitor
from excal.pluginManager import PluginManager
from excal.output import Output


class Analyzer:
    """Analyzer Class, will prepare analysis, call clang to create the AST, translate the AST to astNodes, and call the
    visitor class to get all linter results."""
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

    def printAstRec(self, node: AstNode, printState: int):
        print(node)
        if printState == 2:
            node.printTokens()
        for child in node.children:
            self.printAstRec(child, printState)

    def analyze(self, file_name: str, printAst: int) -> None:
        in_path = self.find_file(file_name)
        # print(f"Parsing {file_name}")
        walker = CWalker(in_path, self.clang_args())
        self.ast = walker.walk()

        visitor = CXXAstNodeVisitor(self.ast, self.pm)
        visitor.visit()
        self.out.addExeptioins(visitor.getExceptions())
        if printAst > 0:
            self.printAstRec(self.ast, printAst)
