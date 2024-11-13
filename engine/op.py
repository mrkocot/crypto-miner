from engine.exception import VerifyFailed
from engine.structs import OpCode

def __bool01(b: bool) -> int:
    if b:
        return 1
    else:
        return 0

def _verify(x: int):
    if x == 0:
        raise VerifyFailed()

def _ifdup(x: int):
    if x == 0:
        return x
    else:
        return [x, x]

def _equal(a, b) -> int:
    return __bool01(a == b)

def _equalverify(a, b) -> int:
    eq = _equal(a, b)
    _verify(eq)
    return eq

def _not(x: int) -> int:
    return __bool01(x == 0)

def _notequal(a, b) -> int:
    return _not(_equal(a, b))

def _booland(a: int, b: int) -> int:
    return __bool01(a != 0 and b != 0)

def _boolor(a: int, b: int) -> int:
    return __bool01(a != 0 or b != 0)


false = OpCode(0, 'OP_FALSE', lambda : 0)
true = OpCode(81, 'OP_TRUE', lambda : 1)
nop = OpCode(97, 'OP_NOP', lambda : None)

ifdup = OpCode(115, 'OP_IFDUP', _ifdup)
drop = OpCode(117, 'OP_DROP', lambda x : None)
dup = OpCode(118, 'OP_DUP', lambda x : [x, x])
nip = OpCode(119, 'OP_NIP', lambda x, y: y)
over = OpCode(120, 'OP_OVER', lambda x, y: [x, y, x])
rot = OpCode(123, 'OP_ROT', lambda x, y, z: [y, z, x])
swap = OpCode(124, 'OP_SWAP', lambda x, y: [y, x])
tuck = OpCode(125, 'OP_TUCK', lambda x, y: [y, x, y])

drop2 = OpCode(109, 'OP_2DUP', lambda x, y: None)
dup2 = OpCode(110, 'OP_2DUP', lambda x, y: [x, y, x, y])
dup3 = OpCode(111, 'OP_3DUP', lambda x, y, z: [x, y, z, x, y, z])

add1 = OpCode(139, 'OP_1ADD', lambda x: x + 1)
sub1 = OpCode(140, 'OP_1SUB', lambda x: x - 1)
negate = OpCode(143, 'OP_NEGATE', lambda x: -x)
abs_ = OpCode(144, 'OP_ABS', lambda x: abs(x))
not_ = OpCode(145, 'OP_NOT', _not)
add = OpCode(147, 'OP_ADD', lambda x, y: x + y)
sub = OpCode(148, 'OP_SUB', lambda x, y: x - y)
# mul = OpCode(149, 'OP_MUL', lambda x, y: x * y)  # DISABLED in bitcoin
# div = OpCode(150, 'OP_DIV', lambda x, y: x // y)  # DISABLED in bitcoin
# mod = OpCode(151, 'OP_MOD', lambda x, y: x % y)  # DISABLED in bitcoin
booland = OpCode(154, 'OP_BOOLAND', _booland)
boolor = OpCode(155, 'OP_BOOLOR', _boolor)
min_ = OpCode(163, 'OP_MIN', min)
max_ = OpCode(164, 'OP_MAX', max)

equal = OpCode(135, 'OP_EQUAL', _equal)
notequal0 = OpCode(146, 'OP_0NOTEQUAL', lambda x : _notequal(x, 0))
numequal = OpCode(156, 'OP_NUMEQUAL', _equal)
numnotequal = OpCode(158, 'OP_NUMNOTEQUAL', _equal)
lessthan = OpCode(159, 'OP_LESSTHAN', lambda x, y: __bool01(x < y))
greaterthan = OpCode(160, 'OP_GREATERTHAN', lambda x, y: __bool01(x > y))
lessthanorequal = OpCode(161, 'OP_LESSTHANOREQUAL', lambda x, y: __bool01(x <= y))
greaterthanorequal = OpCode(162, 'OP_GREATERTHANOREQUAL', lambda x, y: __bool01(x >= y))
within = OpCode(165, 'OP_WITHIN', lambda x, y, z: __bool01(y <= x <= z))

verify = OpCode(105, 'OP_VERIFY', _verify)
equalverify = OpCode(136, 'OP_EQUALVERIFY', _equalverify)
numequalverify = OpCode(157, 'OP_NUMEQUALVERIFY', _equalverify)
