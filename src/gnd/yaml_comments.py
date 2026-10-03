"""Keep ruamel YAML semantics while scanning string comments in linear time.

The two scanner methods below are adapted from ruamel.yaml 0.19.1's
scanner.py. Only comment accumulation/skipping for already validated,
immutable string buffers changes; event semantics and stream fallback remain.

 The MIT License (MIT)

 Copyright (c) 2014-2026 Anthon van der Neut, Ruamel bvba

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""
import re
from typing import Any

from ruamel.yaml.main import CParser
from ruamel.yaml.scanner import _THE_END, RoundTripScanner, Scanner

_COMMENT_END = re.compile(r"[\n\0\r\x85\u2028\u2029]")

def _skip_string_comment(reader):
    if reader.stream is not None or reader.raw_buffer is not None:
        return
    start = reader.pointer
    match = _COMMENT_END.search(reader.buffer, start)
    if match is None:
        return
    n = match.start() - start
    reader.pointer += n
    reader.index += n
    reader.column += n - reader.buffer.count('\uFEFF', start, match.start())

class BulkCommentScanner(RoundTripScanner):
    def scan_to_next_token(self) -> Any:
        # We ignore spaces, line breaks and comments.
        # If we find a line break in the block context, we set the flag
        # `allow_simple_key` on.
        # The byte order mark is stripped if it's the first character in the
        # stream. We do not yet support BOM inside the stream as the
        # specification requires. Any such mark will be considered as a part
        # of the document.
        #
        # TODO: We need to make tab handling rules more sane. A good rule is
        #   Tabs cannot precede tokens
        #   BLOCK-SEQUENCE-START, BLOCK-MAPPING-START, BLOCK-END,
        #   KEY(block), VALUE(block), BLOCK-ENTRY
        # So the checking code is
        #   if <TAB>:
        #       self.allow_simple_keys = False
        # We also need to add the check for `allow_simple_keys == True` to
        # `unwind_indent` before issuing BLOCK-END.
        # Scanners for block, flow, and plain scalars need to be modified.
        srp = self.reader.peek
        srf = self.reader.forward
        if self.reader.index == 0 and srp() == '\uFEFF':
            srf()
        found = False
        white_space = ' \t' if self.flow_level > 0 else ' '
        while not found:
            while srp() in white_space:
                srf()
            ch = srp()
            if ch == '#':
                start_mark = self.reader.get_mark()
                comment_parts = [ch]
                srf()
                # Only the immutable string-input path used by both GND readers.
                # Stream/byte readers retain the original character traversal.
                if self.reader.stream is None and self.reader.raw_buffer is None:
                    match = _COMMENT_END.search(self.reader.buffer, self.reader.pointer)
                    if match is not None and match.start() > self.reader.pointer:
                        length = match.start() - self.reader.pointer
                        comment_parts.append(self.reader.prefix(length))
                        _skip_string_comment(self.reader)
                while ch not in _THE_END:
                    ch = srp()
                    if ch == '\0':  # don't gobble the end-of-stream character
                        # but add an explicit newline as "YAML processors should terminate
                        # the stream with an explicit line break
                        # https://yaml.org/spec/1.2/spec.html#id2780069
                        comment_parts.append('\n')
                        break
                    comment_parts.append(ch)
                    srf()
                # gather any blank lines following the comment
                ch = self.scan_line_break()
                while len(ch) > 0:
                    comment_parts.append(ch)
                    ch = self.scan_line_break()
                end_mark = self.reader.get_mark()
                if not self.flow_level:
                    self.allow_simple_key = True
                return ''.join(comment_parts), start_mark, end_mark
            if self.scan_line_break() != '':
                start_mark = self.reader.get_mark()
                if not self.flow_level:
                    self.allow_simple_key = True
                ch = srp()
                if ch == '\n':  # empty toplevel lines
                    start_mark = self.reader.get_mark()
                    comment = ""
                    while ch:
                        ch = self.scan_line_break(empty_line=True)
                        comment += ch
                    if srp() == '#':
                        # empty line followed by indented real comment
                        comment = comment.rsplit('\n', 1)[0] + '\n'
                    end_mark = self.reader.get_mark()
                    return comment, start_mark, end_mark
            else:
                found = True
        return None

class BulkGuardScanner(Scanner):
    def scan_to_next_token(self) -> Any:
        # We ignore spaces, line breaks and comments.
        # If we find a line break in the block context, we set the flag
        # `allow_simple_key` on.
        # The byte order mark is stripped if it's the first character in the
        # stream. We do not yet support BOM inside the stream as the
        # specification requires. Any such mark will be considered as a part
        # of the document.
        #
        # TODO: We need to make tab handling rules more sane. A good rule is
        #   Tabs cannot precede tokens
        #   BLOCK-SEQUENCE-START, BLOCK-MAPPING-START, BLOCK-END,
        #   KEY(block), VALUE(block), BLOCK-ENTRY
        # So the checking code is
        #   if <TAB>:
        #       self.allow_simple_keys = False
        # We also need to add the check for `allow_simple_keys == True` to
        # `unwind_indent` before issuing BLOCK-END.
        # Scanners for block, flow, and plain scalars need to be modified.
        srp = self.reader.peek
        srf = self.reader.forward
        if self.reader.index == 0 and srp() == '\uFEFF':
            srf()
        found = False
        _the_end = _THE_END
        white_space = ' \t' if self.flow_level > 0 else ' '
        while not found:
            while srp() in white_space:
                srf()
            if srp() == '#':
                _skip_string_comment(self.reader)
                while srp() not in _the_end:
                    srf()
            if self.scan_line_break():
                if not self.flow_level:
                    self.allow_simple_key = True
            else:
                found = True
        return None


def configure_comment_scanner(yaml):
    """Configure an existing safe/round-trip YAML reader without changing its type."""
    if yaml.typ == ["rt"]:
        yaml.Scanner = BulkCommentScanner
    elif yaml.typ == ["safe"] and (CParser is None or yaml.Parser is not CParser):
        yaml.Scanner = BulkGuardScanner
    return yaml
