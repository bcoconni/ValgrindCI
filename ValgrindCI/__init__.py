import argparse
import sys

from .parse import ValgrindData
from .render import HTMLRenderer
from .report import Report

__version__ = "0.4.0"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("xml_file", help="Valgrind XML file name")
    parser.add_argument(
        "--source-dir",
        help="specifies the source directory",
    )
    parser.add_argument(
        "--substitute-path",
        action="append",
        help="specifies a substitution rule `from:to` for finding source files on disk. example: --substitute-path /foo:/bar",
        nargs='?'
    )
    parser.add_argument(
        "--relativize",
        action="append",
        help="specifies a prefix to remove from displayed source filenames. example: --relativize /foo/bar",
        nargs='?'
    )
    parser.add_argument(
        "--relativize-from-substitute-paths",
        default=False,
        action="store_true",
        help="use the `from` values in the substitution rules as prefixes to remove from displayed source filenames",
    )
    parser.add_argument(
        "--output-dir", help="directory where the HTML report will be generated"
    )
    parser.add_argument(
        "--summary",
        default=False,
        action="store_true",
        help="print a summary of errors",
    )
    parser.add_argument(
        "--number-of-errors",
        default=False,
        action="store_true",
        help="print the total number of errors found by Valgrind",
    )
    parser.add_argument(
        "--lines-before",
        default=3,
        type=int,
        help="number of code lines to display in the HTML report before the error line (default to 3)",
    )
    parser.add_argument(
        "--lines-after",
        default=3,
        type=int,
        help="number of code lines to display in the HTML report after the error line (default to 3)",
    )
    parser.add_argument(
        "--abort-on-errors",
        default=False,
        action="store_true",
        help="call exit(1) if errors have been reported by Valgrind",
    )
    args = parser.parse_args()

    data = ValgrindData()
    data.parse(args.xml_file)
    data.set_source_dir(args.source_dir)

    if args.substitute_path:
        substitute_paths = []
        for s in args.substitute_path:
            substitute_paths.append({"from": s.split(":")[0], "to": s.split(":")[1] })
        data.set_substitute_paths(substitute_paths)

    if args.relativize:
        prefixes = []
        for p in args.relativize:
            prefixes.append(p)
        data.set_relative_prefixes(prefixes)

    if args.relativize_from_substitute_paths:
        if not args.substitute_path:
            print("No substitution paths specified on the command line.")
        else:
            prefixes = data._relative_prefixes.copy()
            for s in data._substitute_paths:
                prefixes.append(s.get("from"))
            data.set_relative_prefixes(prefixes)

    errors_total = data.get_num_errors()
    if args.abort_on_errors and errors_total != 0:
        print("{} errors reported by Valgrind - Abort".format(errors_total))
        sys.exit(1)

    if args.output_dir:
        renderer = HTMLRenderer(data)
        renderer.set_source_dir(args.source_dir)
        renderer.render(args.output_dir, args.lines_before, args.lines_after)

    if args.number_of_errors:
        print("{} errors.".format(errors_total))

    if args.summary:
        report = Report(data)
        print(report.summary())
