# Classes to print summary reports of errors reported by Valgrind.
#
# Copyright (c) 2020-2022 Bertrand Coconnier
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

from .parse import ValgrindData


class Report:
    def __init__(self, vg_data: ValgrindData) -> None:
        self._data = vg_data

    def summary(self) -> str:
        s = ""
        for srcfile in sorted(self._data.list_source_files()):
            src_data = self._data.filter_source_file(srcfile)
            s += "{}:\n".format(srcfile)
            s += "{} errors\n".format(src_data.get_num_errors())
            for line in sorted(src_data.list_lines()):
                line_data = src_data.filter_line(line)
                s_line = "\tline {}:".format(line)
                for error in line_data.list_error_kinds():
                    s += "{} {}\t({} errors)\n".format(
                        s_line,
                        error,
                        line_data.filter_error_kind(error).get_num_errors(),
                    )
                    s_line = "\t" + " " * (len(s_line) - 1)
        return s
