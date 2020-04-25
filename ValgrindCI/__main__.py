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

from .parse import ValgrindData
from .render import HTMLRenderer
from .report import Report

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Valgrind XML file name")
parser.add_argument("--source", default=".", help="Specifies the source directory")
parser.add_argument(
    "--summary", default=False, action="store_true", help="Prints a summary"
)
parser.add_argument(
    "--lines-before",
    default=3,
    type=int,
    help="Number of code lines to display before the error line.",
)
parser.add_argument(
    "--lines-after",
    default=3,
    type=int,
    help="Number of code lines to display after the error line.",
)
args = parser.parse_args()

data = ValgrindData()
data.parse(args.input)

renderer = HTMLRenderer(data)
renderer.set_source_dir(args.source)
renderer.render("html", args.lines_before, args.lines_after)

if args.summary:
    report = Report(data)
    print(report.summary())
