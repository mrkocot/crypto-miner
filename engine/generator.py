import math
import random
import secrets
from engine import op, base58
from engine.structs import OpX, OpCode, OpPushBytes, TxInput, TxOutput, Transaction
from engine.settings import *

def weighed_choice(options: dict):
    total = sum(options.values())
    r = random.randint(1, total)
    upto = 0
    for o, w in options.items():
        upto += w
        if upto >= r:
            return o
        upto += w
    assert False, "weighed_choice failed to pick an option"

def yes_or_no(percent_chance: int) -> bool:
    return random.randint(1, 100) <= percent_chance

############################# SCRIPT ###################################

def _random_offset(base_value: int, down: int, up: int, avoid_base: bool = True) -> int:
    lowest = max(base_value + down, -1)
    highest = min(base_value + up, 127)
    rand = random.randint(lowest, highest)
    while rand == base_value and avoid_base:
        rand = random.randint(lowest, highest)
    return rand


_reductions = {
    op.drop: 1,
    op.nip: 1,
    op.add: 1,
    op.sub: 1,
    op.booland: 1,
    op.boolor: 1,
    op.min_: 1,
    op.max_: 1,
}

_neutrals = {
    op.rot: 1,
    op.swap: 1,
    op.add1: 1,
    op.sub1: 1,
    op.negate: 1,
    op.abs_: 1,
    op.not_: 1,
    op.nop: 1,
}

_expansions = {
    0: 1,  # adding one number to the stack
    op.ifdup: 1,
    op.dup: 1,
    op.over: 1,
    op.tuck: 1,
}

_finishers = {
    op.numequal: 1,
    op.numnotequal: 1,
    op.greaterthan: 1,
    op.greaterthanorequal: 1,
    op.lessthan: 1,
    op.lessthanorequal: 1,
}


def get_last_item(result: int, finisher: OpCode, correct: bool) -> int:
    if (finisher.name == 'OP_NUMEQUAL' and correct) or (finisher.name == 'OP_NUMNOTEQUAL' and not correct):
        return result
    elif (finisher.name == 'OP_NUMNOTEQUAL' and correct) or (finisher.name == 'OP_NUMEQUAL' and not correct):
        return _random_offset(base_value=result, down=-10, up=10)
    elif (finisher.name == 'OP_GREATERTHAN' and correct) or (finisher.name == 'OP_LESSTHANOREQUAL' and not correct):
        return _random_offset(base_value=result, down=-10, up=-1)
    elif (finisher.name == 'OP_LESSTHANOREQUAL' and correct) or (finisher.name == 'OP_GREATERTHAN' and not correct):
        return _random_offset(base_value=result, down=0, up=10, avoid_base=False)
    elif (finisher.name == 'OP_LESSTHAN' and correct) or (finisher.name == 'OP_GREATERTHANOREQUAL' and not correct):
        return _random_offset(base_value=result, down=1, up=10)
    elif (finisher.name == 'OP_GREATERTHANOREQUAL' and correct) or (finisher.name == 'OP_LESSTHAN' and not correct):
        return _random_offset(base_value=result, down=-10, up=0, avoid_base=False)
    else:
        raise ValueError(f'Unknown finisher: {finisher}')

def generate_arithmetic_script(correct: bool) -> list[OpCode]:  # if correct is False, the script should fail the verification
    instructions = []
    stack = []
    strategy = {'reduce': 0, 'keep': SCRIPT_LENGTH, 'expand': 2 * SCRIPT_LENGTH}
    for _ in range(2):  # two starting items
        starting_item = random.randint(-1, 16)
        instructions.append(OpX(starting_item))
        stack.append(starting_item)
    while len(stack) > 1:
        step = weighed_choice(strategy)
        if step == 'reduce':
            operation = weighed_choice(_reductions)
        elif step == 'expand':
            operation = weighed_choice(_expansions)
            if operation == 0:
                item = random.randint(-1, 16)
                operation = OpX(item)
        else:
            operation = weighed_choice(_neutrals)

        try:
            operation.apply(stack)
            instructions.append(operation)
            if strategy['expand'] > 1:  # the longer we go, the lower the chance of expansion
                strategy['expand'] -= 1
                strategy['reduce'] += 1
        except (ValueError, IndexError):
            # print(f'W | Operation {operation} not added: {e}')
            pass
    result = stack[0]

    finisher = weighed_choice(_finishers)
    precise_finisher = finisher.name in ('OP_NUMEQUAL', 'OP_NUMNOTEQUAL')
    if result < -1 or (result == -1 and not precise_finisher):  # we don't like negative numbers - negate those
        instructions.append(op.negate)
        result = -result
    if 0 <= result <= 126 or (precise_finisher and result in (-1, 127)):  # leaving -1 and 127 as margins for < or >
        last_item = get_last_item(result, finisher, correct)
        if -1 <= last_item <= 16:
            instructions.append(OpX(last_item))
        else:
            instructions.append(OpPushBytes(hex(last_item)[2:]))
    else:  # result is outside the safe range, we just verify it
        if not correct:
            instructions.append(op.not_)  # result will never be zero, so we have to OP_NOT it if not correct
        finisher = op.verify

    instructions.append(finisher)
    return instructions

############################# TX ###################################

_errors = {
    'none': 6,
    'script_failed': 1,
    'negative_fee': 1,
    'invalid_input': 1,
    'already_spent': 1,
}

def _random_sha1() -> str:
    return secrets.token_hex(32)

def _random_tx_id() -> str:
    return base58.encode(_random_sha1())

def _generate_valid_io_pair(script_ok: bool) -> tuple[TxOutput, TxInput]:  # (external output, our input)
    script = generate_arithmetic_script(script_ok)
    amount = random.randint(10, 2_500) * (10 ** random.randint(1, 5))
    tx_id = _random_tx_id()
    index = random.randint(0, 4)
    a = TxOutput(tx_id, index, script[2:], amount)
    b = TxInput(tx_id, index, script[:2])
    return a, b

def _generate_fake_sources(tx_id: str, real_index: int) -> list[TxOutput]:  # no-op for real_index<=0
    ret: list[TxOutput] = []
    indices_after = random.randint(0, 2)
    fake_indices = range(0, real_index + indices_after)
    for i in fake_indices:
        if i == real_index:
            continue
        script = generate_arithmetic_script(correct=False)[2:]
        amount = random.randint(10, 2_500) * (10 ** random.randint(1, 5))
        out = TxOutput(tx_id, i, script, amount)
        out.spent = yes_or_no(30)
        ret.append(out)
    return ret

def _divide(total: int) -> list[int]:
    divisions = random.randint(1, 4)
    ends = [total]
    for _ in range(divisions - 1):
        new_end = random.randint(0, total)
        ends.append(new_end)
    ends.sort()
    for i in range(divisions - 1, 0, -1):
        ends[i] -= ends[i - 1]
    return ends

def _generate_output(index: int, amount: int) -> TxOutput:
    tx_id = _random_tx_id()
    script = [op.verify]
    return TxOutput(tx_id, index, script, amount)

def generate_tx(source_list: list[TxOutput]) -> Transaction:
    error = weighed_choice(_errors)
    script_ok = error != 'script_failed'
    src, inp = _generate_valid_io_pair(script_ok=script_ok)
    if error != 'invalid_input' or yes_or_no(50):  # always if not invalid input, 50% chance otherwise
        source_list.extend(_generate_fake_sources(src.tx_id, src.index))  # add fake lower-index sources
    if error != 'invalid_input':
        if error == 'already_spent':
            src.spent = True
        source_list.append(src)
    amount = src.amount
    if error == 'negative_fee':
        fee_factor = .01 * random.randint(-20, -5)
    else:
        fee_factor = .01 * random.randint(10, 50)
    fee = math.ceil(fee_factor * amount)
    netto = amount - fee
    output_amounts = _divide(netto)
    outputs = [_generate_output(i, a) for i, a in enumerate(output_amounts)]
    return Transaction(_random_tx_id(), inp, outputs, amount, fee, error)
