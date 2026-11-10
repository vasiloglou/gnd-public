import sys
from pathlib import Path

from ossie_ontology.parser import OssieParser

parser = OssieParser()
try:
    parser.parse(Path(sys.argv[1]))
except (ValueError, TypeError, KeyError, RuntimeError, SyntaxError) as error:
    print(type(error).__name__ + ": " + str(error))
    raise SystemExit(1) from None
print("OssieParser accepted the ontology")
