# Main function of ValgrindCI.
#
# Copyright (c) 2020 Bertrand Coconnier
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>
#

import argparse

from . import __version__
from .parse import ValgrindData
from .render import HTMLRenderer
from .report import Report


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
    args = parser.parse_args()

    data = ValgrindData()
    data.parse(args.xml_file)

    if args.output_dir:
        renderer = HTMLRenderer(data)
        renderer.set_source_dir(args.source)
        renderer.render(args.output_dir, args.lines_before, args.lines_after)

    if args.number_of_errors:
        print("{} errors.".format(data.get_num_errors()))

    if args.summary:
        report = Report(data)
        print(report.summary())


if __name__ == "__main__":
    main()
