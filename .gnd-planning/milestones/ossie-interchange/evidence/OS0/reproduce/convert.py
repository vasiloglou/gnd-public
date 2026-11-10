import ast
import json
import os
import socket
import sys
from pathlib import Path

config, document, output = map(Path, sys.argv[1:])
os.environ["RAI_CONFIG_FILE_PATH"] = str(config.resolve())


def deny(*args, **kwargs):
    raise RuntimeError("OS0 offline control refused a socket connection")


socket.socket.connect = deny
socket.socket.connect_ex = deny
socket.create_connection = deny
try:
    socket.create_connection(("example.invalid", 443))
except RuntimeError as error:
    assert "OS0 offline control" in str(error)
else:
    raise AssertionError("network guard was not active")

from ossie_ontology.parser import OssieParser
from ossie_relationalai import OssieToRelationalAIConverter, declared_table
from relationalai.semantics.metamodel.pyrel_codegen import to_pyrel

model = OssieToRelationalAIConverter.convert(
    OssieParser().parse(document),
    table_provider=declared_table,
)
source = to_pyrel(model.base_model().to_metamodel())
output.write_text(source)
calls = [
    (node.lineno, node)
    for node in ast.walk(ast.parse(source))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
]
print(
    json.dumps(
        {
            "concepts": [
                ast.unparse(node.args[0]) if node.args else ast.unparse(node)
                for _, node in sorted(calls, key=lambda item: item[0])
                if node.func.attr == "Concept"
            ],
            "properties": [
                ast.unparse(node.args[0]) if node.args else ast.unparse(node)
                for _, node in sorted(calls, key=lambda item: item[0])
                if node.func.attr in {"Property", "Relationship"}
            ],
            "require_count": sum(node.func.attr == "require" for _, node in calls),
            "offline_control": "socket connection refused before importing the converter",
        }
    )
)
