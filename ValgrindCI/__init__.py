import argparse
import sys

from .parse import ValgrindData
from .render import HTMLRenderer
from .report import Report

__version__ = "0.1.0"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("xml_file", help="Valgrind XML file name")
    parser.add_argument(
        "--source-dir", help="specifies the source directory",
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
