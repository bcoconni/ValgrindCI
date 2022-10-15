# Classes to parse XML output files from Valgrind.
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

import os.path
from typing import List, Optional

import defusedxml.ElementTree as et


class Error:
    def __init__(self, tag) -> None:
        self.stack: List[Frame] = []
        # bugfix-issue#1: valgrind 3.15.0 does not generate
        # [what] xml tag, [xwhat] is generated instead
        what_tag = tag.find("what")
        if what_tag is not None:
            self.what: str = what_tag.text
        else:
            what_tag = tag.find("xwhat/text")
            if what_tag is None:
                raise ValueError(
                    "Cannot find either <what> or <xwhat> tags, "
                    "please report this issue "
                    "to the ValgrindCI project on GitHub."
                )
            else:
                self.what = what_tag.text
        self.kind: str = tag.find("kind").text
        self.unique = int(tag.find("unique").text, 16)
        for frame in tag.find("stack").findall("frame"):
            if frame.find("obj") is not None:
                self.stack.append(Frame(frame))

        self.auxstack: List[Frame] = []
        self.auxwhat: Optional[str] = None
        auxwhat = tag.find("auxwhat")
        stack_2 = tag.find("./stack[2]")
        if auxwhat is not None and stack_2 is not None:
            self.auxwhat = auxwhat.text
            for frame in stack_2.findall("frame"):
                if frame.find("obj") is not None:
                    self.auxstack.append(Frame(frame))

    def __str__(self) -> str:
        s = f"{self.what} (0x{self.unique:x})"
        for i, frame in enumerate(self.stack):
            s += f"\n#{i} => {frame}"
        if self.auxwhat is not None:
            s += f"\n\nAuxilliary:\n{self.auxwhat}"
            for i, frame in enumerate(self.auxstack):
                s += f"\n#{i} => {frame}"
        return s

    def find_first_source_reference(self, source_dir: Optional[str]) -> Optional[int]:
        for i, frame in enumerate(self.stack):
            filename = frame.get_path(None)
            if filename is not None and os.path.isabs(filename):
                if (
                    source_dir is None
                    or os.path.commonpath([source_dir, filename]) == source_dir
                ):
                    return i
        return None


class Frame:
    def __init__(self, tag) -> None:
        self.obj = tag.find("obj").text
        func = tag.find("fn")
        if func is not None:
            self.func: Optional[str] = tag.find("fn").text
        else:
            self.func = None
        folder = tag.find("dir")
        if folder is not None:
            self.folder: Optional[str] = folder.text
            source_file = tag.find("file")
            line = tag.find("line")
            assert source_file is not None
            assert line is not None
            self.filename: Optional[str] = source_file.text
            self.line: Optional[int] = int(line.text)
        else:
            self.folder = None
            self.filename = None
            self.line = None

    def __str__(self) -> str:
        if self.folder is not None:
            return "{}:{}".format(self.get_path(None), self.line)
        return self.func or ""

    def get_path(self, source_dir: Optional[str]) -> Optional[str]:
        if self.folder is not None and self.filename is not None:
            filename = os.path.join(self.folder, self.filename)
            if source_dir is not None:
                filename = os.path.relpath(filename, source_dir)
            return filename
        return None


class ValgrindData:
    def __init__(self) -> None:
        self.errors: List[Error] = []
        self._source_dir: Optional[str] = None

    def parse(self, xml_file: str) -> None:
        root = et.parse(xml_file).getroot()
        for error_tag in root.findall("error"):
            self.errors.append(Error(error_tag))

    def set_source_dir(self, source_dir: Optional[str]) -> None:
        if source_dir is not None:
            self._source_dir = os.path.abspath(source_dir)
        else:
            self._source_dir = None

    def get_num_errors(self) -> int:
        if self._source_dir is None:
            return len(self.errors)

        num_errors = 0
        if self._source_dir is None:
            return len(self.errors)

        for error in self.errors:
            if error.find_first_source_reference(self._source_dir) is not None:
                num_errors += 1
        return num_errors

    def filter_error_kind(self, kind: str) -> ValgrindData:
        data: ValgrindData = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            if error.kind == kind:
                data.errors.append(error)
        return data

    def filter_source_file(self, filename: str) -> ValgrindData:
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            if error.stack[f].get_path(self._source_dir) == filename:
                data.errors.append(error)
        return data

    def filter_line(self, line: int) -> ValgrindData:
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            if error.stack[f].line == line:
                data.errors.append(error)
        return data

    def filter_function(self, function: str) -> ValgrindData:
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                f = 0

            if error.stack[f].func == function:
                data.errors.append(error)
        return data

    def list_error_kinds(self) -> List[str]:
        error_kinds = []
        for error in self.errors:
            if error.kind not in error_kinds:
                error_kinds.append(error.kind)
        return error_kinds

    def list_source_files(self) -> List[str]:
        source_files = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            filename = error.stack[f].get_path(self._source_dir)
            if filename is not None and filename not in source_files:
                source_files.append(filename)
        return source_files

    def list_lines(self) -> List[int]:
        lines = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            line = error.stack[f].line
            if line is not None and line not in lines:
                lines.append(line)
        return lines

    def list_functions(self) -> List[str]:
        functions = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                f = 0

            func = error.stack[f].func
            if func is not None and func not in functions:
                functions.append(func)
        return functions
