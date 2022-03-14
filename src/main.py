"""EXCAL - Extendable Clang AST based Linter."""
import os
import glob
from typing import List
import configparser

from argparse import ArgumentParser
from analyzer import Analyzer
from pluginManager import PluginManager
from output import Output


def readConfig(args):
    if len(args.files) != 1:
        return args

    path: str = args.files[0]

    if not os.path.isdir(path):
        return args
    if not os.path.exists(f"{path}setup.cfg"):
        return args

    config = configparser.ConfigParser()
    config.read(f"{path}setup.cfg")

    if 'EXCAL' not in config.sections():
        return args

    cfg = config['EXCAL']
    for key in cfg:
        if key == "force_cpp":
            args.force_cpp = cfg[key] == 'True'
        if key == "includes":
            args.include.extend([l.strip() for l in cfg[key].split('\n')])
        if key == "exclude_files":
            args.exclude_files.extend(
                [f'{args.files[0]}{line.strip()}'
                 for line in cfg[key].split('\n') if line != ''])
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

    args = parser.parse_args()

    args = readConfig(args)

    clang_args = args.args

    if args.argfile is not None:
        with open(args.argfile, "r") as fl:
            lines = [ln.strip() for ln in fl.readlines()]
            clang_args.extend(lines)

    if args.force_cpp:
        clang_args.extend(['-x', 'c++'])

    if args.extensions != []:
        FILE_EXTENSIONS = args.extensions
    else:
        FILE_EXTENSIONS: List[str] = ["c", "h", "cpp", "hpp"]

    exfiles = set()
    for ex_file in args.exclude_files:
        if not os.path.isfile(ex_file):
            for ext in FILE_EXTENSIONS:
                exfiles |= set(glob.glob(f"{ex_file}/**/*.{ext}", recursive=True))
        else:
            exfiles.add(ex_file)

    analyze_files = []
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

    for in_file in analyze_files:
        analyzer.analyze(in_file, args.print_tree)

    out.printError()


if __name__ == "__main__":
    main()
