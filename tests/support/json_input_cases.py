import json
from decimal import Decimal


def nested(count):
    value = 0
    for _ in range(count):
        value = [value]
    return value

def value(variant):
    if variant == 'cycle':
        result = []
        result.append(result)
        return {'v': result}
    selected = {'exact': lambda: [1, Decimal('1.0'), Decimal('1E+100'), -10 ** 127, None, True], 'depth64': lambda: nested(63), 'depth65': lambda: nested(64), 'scalar4096': lambda: 'x' * 4096, 'scalar4097': lambda: 'x' * 4097, 'multi4096': lambda: 'é' * 2048, 'multi4097': lambda: 'é' * 2048 + 'x', 'digits128': lambda: 10 ** 127, 'digits129': lambda: 10 ** 128, 'giant-int': lambda: 10 ** 5000, 'nonfinite': lambda: float('inf'), 'unsupported': lambda: object(), 'nonstring-key': lambda: {1: 2}, 'surrogate': lambda: '\ud800'}
    return {'v': selected[variant]()}

def raw(variant):
    cap = 10 * 1024 * 1024
    values = {'exact': b'[1,1.0,1e100,-1.25,null,true]', 'quoted': b'{"v":"[[[[\\"{{{{"}', 'utf16': '{"v":1.0}'.encode('utf-16'), 'bytes-at': b'0' + b' ' * 31, 'bytes-over': b'0' + b' ' * 32, 'depth64': b'[' * 64 + b'0' + b']' * 64, 'depth65': b'[' * 65 + b'0' + b']' * 65, 'digits128': b'1' + b'0' * 127, 'negative128': b'-1' + b'0' * 127, 'digits129': b'1' + b'0' * 128, 'duplicate': b'{"v":0,"v":1}', 'bad-utf8': b'"\xff"', 'surrogate': b'"\\ud800"', 'nonfinite': b'[NaN,Infinity]', 'extreme-exponent': b'1e9999999999999999999', 'byte-before-depth': b'[' * 65, 'raw-near-cap': b'0' + b' ' * (cap - 1)}
    if variant.startswith(('scalar', 'multi')):
        return json.dumps(value(variant)['v'], ensure_ascii=False).encode()
    return values[variant]
