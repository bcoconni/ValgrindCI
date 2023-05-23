# Classes to render Valgrind errors in an HTML report.
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

import os
import shutil
from typing import Any, Dict, List, Optional, Tuple

from jinja2 import Environment, PackageLoader, select_autoescape

from .parse import ValgrindData


class HTMLRenderer:
    def __init__(self, vg_data: ValgrindData) -> None:
        self._data = vg_data
        env = Environment(
            loader=PackageLoader("ValgrindCI", "data"),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._source_tmpl = env.get_template("source_file.html")
        self._index_tmpl = env.get_template("index.html")
        self._source_dir: Optional[str] = None

    def set_source_dir(self, source_dir: Optional[str]) -> None:
        if source_dir is not None:
            self._source_dir = os.path.abspath(source_dir)
        else:
            self._source_dir = None

    def render(self, report_title: str, output_dir: str, lines_before: int, lines_after: int) -> None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "data", "valgrind.css"), output_dir
        )
        shutil.copy(
            os.path.join(os.path.dirname(__file__), "data", "valgrind.js"), output_dir
        )

        summary = []
        total_num_errors = 0

        for source_file in sorted(self._data.list_source_files()):
            try:
                lines_of_code, num_errors = self._extract_data_per_source_file(
                    source_file, lines_before, lines_after
                )
            except FileNotFoundError:
                continue

            html_filename = self._unique_html_filename(source_file)

            with open(os.path.join(output_dir, html_filename), "w") as f:
                f.write(
                    self._source_tmpl.render(
                        num_errors=num_errors,
                        source_file_name=self._data.relativize(source_file),
                        codelines=lines_of_code,
                    )
                )

            summary.append(
                {
                    "filename": self._data.relativize(source_file),
                    "errors": num_errors,
                    "link": html_filename,
                }
            )
            total_num_errors += num_errors

        with open(os.path.join(output_dir, "index.html"), "w") as f:
            f.write(
                self._index_tmpl.render(
                    title=report_title,
                    source_list=summary,
                    num_errors=total_num_errors
                )
            )

    def _unique_html_filename(self, source_file: str) -> str:
        # TODO: Make sure that there are no clashes between 2 files with the same
        # name and located in different directories.
        name = os.path.splitext(os.path.basename(source_file))
        return name[0] + "_" + name[1][1:] + ".html"

    def _extract_error_data(
        self,
        source_data: ValgrindData,
        line_number: int,
        lines_before: int,
        lines_after: int,
    ) -> Dict[str, Any]:
        current_error = source_data.filter_line(line_number).errors[0]
        issue: Dict[str, Any] = {"stack": [], "what": current_error.what}
        initial_frame = current_error.find_first_source_reference(self._source_dir)
        assert initial_frame is not None
        for frame in current_error.stack[initial_frame + 1 :]:
            stack: Dict[str, Any] = {}
            fullname = frame.get_path(None)
            stack["code"] = []
            stack["function"] = frame.func
            if fullname is None:
                stack["fileref"] = frame.func
            else:
                error_line = frame.line
                assert error_line is not None
                stack["line"] = error_line - lines_before - 1
                stack["error_line"] = lines_before + 1
                frame_source = frame.get_path(self._source_dir)
                frame_source = self._data.relativize(frame_source)
                stack["fileref"] = "{}:{}".format(frame_source, error_line)
                fullname = self._data.substitute_path(fullname)
                try:
                    with open(fullname, "r", errors="replace") as f:
                        for l, code_line in enumerate(f.readlines()):
                            if l >= stack["line"] and l <= error_line + lines_after - 1:
                                stack["code"].append(code_line)
                except OSError as e:
                    print(f"Warning: cannot read stack data from missing source file: {e.filename}")
            issue["stack"].append(stack)
        return issue

    def _extract_data_per_source_file(
        self, source_file: str, lines_before: int, lines_after: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        src_data = self._data.filter_source_file(source_file)
        error_lines = sorted(src_data.list_lines())
        lines_of_code = []

        if self._source_dir is not None:
            filename = os.path.join(self._source_dir, source_file)
        else:
            filename = source_file

        filename = self._data.substitute_path(filename)
        try:
            with open(filename, "r", errors="replace") as f:
                for l, line in enumerate(f.readlines()):
                    klass = None
                    issue = None
                    if l + 1 in error_lines:
                        klass = "error"
                        issue = self._extract_error_data(
                            src_data, l + 1, lines_before, lines_after
                        )
                    lines_of_code.append(
                        {"line": line[:-1], "klass": klass, "issue": issue}
                    )
        except OSError as e:
            print(f"Warning: cannot extract data from missing source file: {e.filename}")
        return lines_of_code, len(error_lines)
