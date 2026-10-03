import io

import pytest
from ruamel.yaml import YAML
from ruamel.yaml.reader import Reader

from gnd.yaml_comments import BulkCommentScanner, BulkGuardScanner


class MeasuredBuffer(str):
    copied = 0

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if isinstance(key, slice):
            type(self).copied += len(value)
        return value


class MeasuredReader(Reader):
    @Reader.stream.setter
    def stream(self, value):
        Reader.stream.fset(self, value)
        if isinstance(value, str):
            self.buffer = MeasuredBuffer(self.buffer)


@pytest.mark.parametrize('kind,scanner', [('safe', BulkGuardScanner), ('rt', BulkCommentScanner)])
def test_short_comment_scanning_keeps_buffer_copying_linear(kind, scanner):
    text = '# x\n' * 4096 + 'key: value\n'
    yaml = YAML(typ=kind)
    yaml.Reader = MeasuredReader
    yaml.Scanner = scanner
    MeasuredBuffer.copied = 0
    document = yaml.load(text)
    assert document['key'] == 'value'
    assert MeasuredBuffer.copied <= 3 * len(text)
    if kind == 'rt':
        output = io.StringIO()
        yaml.dump(document, output)
        assert output.getvalue() == text
