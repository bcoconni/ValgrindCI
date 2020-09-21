# Classes to parse XML output files from Valgrind.
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

import os.path
import defusedxml.ElementTree as et


class Error:
    def __init__(self, tag):
        self.stack = []
        # bugfix-issue#1: valgrind 3.15.0 does not generate
        # [what] xml tag, [xwhat] is generated instead
        self.what = tag.find("what")
        if self.what is None:
            self.what = tag.find("xwhat")
        if self.what is None:
            raise ValueError("looks like valgrind xml file format changed, "
                             "please report this issue "
                             "on the ValgrindCI github page.")
        self.what = self.what.text
        self.kind = tag.find("kind").text
        self.unique = int(tag.find("unique").text, 16)
        for frame in tag.find("stack").findall("frame"):
            self.stack.append(Frame(frame))
        self.auxstack = []
        self.auxwhat = tag.find("auxwhat")
        if self.auxwhat is not None:
            self.auxwhat = self.auxwhat.text
            for frame in tag.find("./stack[2]").findall("frame"):
                self.auxstack.append(Frame(frame))

    def __str__(self):
        s = f"{self.what} (0x{self.unique:x})"
        for i, frame in enumerate(self.stack):
            s += f"\n#{i} => {frame}"
        if self.auxwhat is not None:
            s += f"\n\nAuxilliary:\n{self.auxwhat}"
            for i, frame in enumerate(self.auxstack):
                s += f"\n#{i} => {frame}"
        return s

    def find_first_source_reference(self, source_dir):
        for i, frame in enumerate(self.stack):
            filename = frame.get_path(None)
            if filename is not None:
                if (
                    source_dir is None
                    or os.path.commonpath([source_dir, filename]) == source_dir
                ):
                    return i
        return None


class Frame:
    def __init__(self, tag):
        self.obj = tag.find("obj").text
        func = tag.find("fn")
        if func is not None:
            self.func = tag.find("fn").text
        else:
            self.func = None
        folder = tag.find("dir")
        if folder is not None:
            self.folder = folder.text
            source_file = tag.find("file")
            line = tag.find("line")
            assert source_file is not None
            assert line is not None
            self.filename = source_file.text
            self.line = int(line.text)
        else:
            self.folder = None
            self.filename = None
            self.line = None

    def __str__(self):
        if self.folder is not None:
            return "{}:{}".format(self.get_path(None), self.line)
        return self.func

    def get_path(self, source_dir):
        if self.folder is not None:
            filename = os.path.join(self.folder, self.filename)
            if source_dir is not None:
                filename = os.path.relpath(filename, source_dir)
            return filename
        return None


class ValgrindData:
    def __init__(self):
        self.errors = []
        self._source_dir = None

    def parse(self, xml_file):
        root = et.parse(xml_file).getroot()
        for error_tag in root.findall("error"):
            self.errors.append(Error(error_tag))

    def set_source_dir(self, source_dir):
        if source_dir is not None:
            self._source_dir = os.path.abspath(source_dir)
        else:
            self._source_dir = None

    def get_num_errors(self):
        num_errors = 0
        for error in self.errors:
            if error.find_first_source_reference(self._source_dir) is not None:
                num_errors += 1
        return num_errors

    def filter_error_kind(self, kind):
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            if error.kind == kind:
                data.errors.append(error)
        return data

    def filter_source_file(self, filename):
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            if error.stack[f].get_path(self._source_dir) == filename:
                data.errors.append(error)
        return data

    def filter_line(self, line):
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            if error.stack[f].line == line:
                data.errors.append(error)
        return data

    def filter_function(self, function):
        data = ValgrindData()
        data._source_dir = self._source_dir
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                f = 0

            if error.stack[f].func == function:
                data.errors.append(error)
        return data

    def list_error_kinds(self):
        error_kinds = []
        for error in self.errors:
            if error.kind not in error_kinds:
                error_kinds.append(error.kind)
        return error_kinds

    def list_source_files(self):
        source_files = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            filename = error.stack[f].get_path(self._source_dir)
            if filename not in source_files:
                source_files.append(filename)
        return source_files

    def list_lines(self):
        lines = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                continue
            line = error.stack[f].line
            if line not in lines:
                lines.append(line)
        return lines

    def list_functions(self):
        functions = []
        for error in self.errors:
            f = error.find_first_source_reference(self._source_dir)
            if f is None:
                f = 0

            func = error.stack[f].func
            if func not in functions:
                functions.append(func)
        return functions
