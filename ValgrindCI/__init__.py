import argparse
import sys

from .parse import ValgrindData
from .render import HTMLRenderer
from .report import Report

__version__ = "0.0.1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("xml_file", help="Valgrind XML file name")
    parser.add_argument(
        "--source",
        default=".",
        help="Specifies the source directory (default to working directory)",
    )
    parser.add_argument(
        "--output-dir", help="Directory the HTML report will be written."
    )
    parser.add_argument(
        "--summary", default=False, action="store_true", help="Prints a summary"
    )
    parser.add_argument(
        "--number-of-errors",
        default=False,
        action="store_true",
        help="Prints the total number of error found by Valgrind.",
    )
    parser.add_argument(
        "--lines-before",
        default=3,
        type=int,
        help="Number of code lines to display before the error line. (default to 3)",
    )
    parser.add_argument(
        "--lines-after",
        default=3,
        type=int,
        help="Number of code lines to display after the error line. (default to 3)",
    )
    parser.add_argument(
        "--abort-on-errors",
        default=False,
        action="store_true",
        help="Call exit(1) if errors have been reported by Valgrind.",
    )
    args = parser.parse_args()

    data = ValgrindData()
    data.parse(args.xml_file)

    if args.abort_on_errors and data.get_num_errors() != 0:
        sys.exit(1)

    if args.output_dir:
        renderer = HTMLRenderer(data)
        renderer.set_source_dir(args.source)
        renderer.render(args.output_dir, args.lines_before, args.lines_after)

    if args.number_of_errors:
        print("{} errors.".format(data.get_num_errors()))

    if args.summary:
        report = Report(data)
        print(report.summary())
