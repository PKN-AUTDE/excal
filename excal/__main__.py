"""EXCAL - Extendable Clang AST based Linter."""
import os
from pathlib import Path
import glob
from typing import List
import configparser
from argparse import ArgumentParser

from excal.analyzer import Analyzer
from excal.pluginManager import PluginManager
from excal.output import Output


def findConfig(path: str, find_config: bool) -> str:

    if os.path.exists(f"{path}setup.cfg"):
        return path
    if not find_config:
        return ""

    walkPath = Path(path)
    # parent function will return previous path if no parent exists so this checks if root node exists.
    while walkPath.parent != path:
        walkPath = walkPath.parent
        if os.path.exists(f"{str(walkPath)}/setup.cfg"):
            return str(walkPath) + "/"
    return ""


def readConfig(args):
    if len(args.files) != 1:
        return args

    path: str = args.files[0]

    if not os.path.isdir(path) and not args.find_config:
        return args
    if not path.endswith('/') and not path.endswith('\\'):
        path += '/'
    if not os.path.exists(f"{path}setup.cfg") and not args.find_config:
        return args

    config = configparser.ConfigParser()
    configPath = findConfig(path, args.find_config)
    if configPath == "":
        return args

    config.read(f"{configPath}setup.cfg")

    if 'EXCAL' not in config.sections():
        return args

    cfg = config['EXCAL']
    for key in cfg:
        if key == "force_cpp":
            args.force_cpp = cfg[key] == 'True'
        if key == "includes":
            args.include.extend([l.strip() for l in cfg[key].split('\n')])
        if key == "exclude_files" and not args.find_config:
            args.exclude_files.extend(
                [f'{path}{line.strip()}'
                 for line in cfg[key].split('\n') if line != ''])
        # files überschreiben das directory. Wenn dieses auch gescannt werden soll, muss es auch eingefügt werden.
        if key == "parse_files" and not args.find_config:
            args.files = [f'{path}{line.strip()}'
                          for line in cfg[key].split('\n') if line != '']

    return args


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--args", "-a", nargs="*", required=False,
                        default=[], help="Additional clang arguments")
    parser.add_argument("--argfile", type=str, default=None, required=False,
                        help="File containing clang arguments")
    parser.add_argument("--include", "-i", nargs="+", required=False, default=[],
                        help="include directories")
    parser.add_argument("--files", "-f", nargs="+", required=True,
                        help="File to translate")
    parser.add_argument("--exclude-files", "-e", nargs="+", required=False, default=[],
                        help="files within files directory, that should be ignored")
    parser.add_argument("--print-tree", "-p", nargs='?', required=False,
                        const=True, default=False, help="print AST of input files")
    parser.add_argument("--force-cpp", "-cpp", nargs='?', required=False,
                        const=True, default=False,
                        help="forces files to be analyzed as C++ files.")
    parser.add_argument("--extensions", "-ext", nargs="+", required=False,
                        default=[], help="file extensions to parse.")
    parser.add_argument("--print-token-tree", "-ptt", nargs='?', required=False,
                        const=True, default=False, help="print AST plus corresponding Tokens")
    parser.add_argument("--output-style", "-out", choices=['stdErr', 'json'], required=False,
                        default='stdErr', help="file extensions to parse.")
    parser.add_argument("--find-config", "-fcfg", nargs='?', required=False,
                        const=True, default=False,
                        help="Will try and find a setup.cfg file in parents directories of input-file. Will ignore\
                        parse_files and exclude_files options in .cfg file, as it may be used for single files.")

    args = parser.parse_args()

    args = readConfig(args)

    clang_args = args.args

    if args.argfile is not None:
        with open(args.argfile, "r") as fl:
            lines = [ln.strip() for ln in fl.readlines()]
            clang_args.extend(lines)

    if args.force_cpp:
        clang_args.extend(['-x', 'c++'])

    FILE_EXTENSIONS: List[str] = []
    if args.extensions != []:
        FILE_EXTENSIONS = args.extensions
    else:
        FILE_EXTENSIONS = ["c", "h", "cpp", "hpp"]

    exfiles = set()
    for ex_file in args.exclude_files:
        if not os.path.isfile(ex_file):
            for ext in FILE_EXTENSIONS:
                exfiles |= set(glob.glob(f"{ex_file}/**/*.{ext}", recursive=True))
        else:
            exfiles.add(ex_file)

    analyze_files: List[str] = []
    for in_file in args.files:
        if os.path.isdir(in_file):
            for ext in FILE_EXTENSIONS:
                new_files = glob.glob(f"{in_file}/**/*.{ext}", recursive=True)
                analyze_files = analyze_files + [f for f in new_files if f not in exfiles]
        else:
            analyze_files = analyze_files + [in_file]

    pm: PluginManager = PluginManager()
    pm.loadPlugins()
    out: Output = Output()
    analyzer = Analyzer(args.include, clang_args, pm, out)

    printState = 0
    if(args.print_tree):
        printState = 1
    if(args.print_token_tree):
        printState = 2

    for in_file in analyze_files:
        analyzer.analyze(in_file, printState)

    if args.output_style == 'stdErr':
        out.printError()
    if args.output_style == "json":
        out.printJson()


if __name__ == "__main__":
    main()
