import random
from engine import op
from engine.structs import OpX, OpCode, OpPushBytes

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
        return _random_offset(base_value=result, down=1, up=10)
    elif (finisher.name == 'OP_LESSTHANOREQUAL' and correct) or (finisher.name == 'OP_GREATERTHAN' and not correct):
        return _random_offset(base_value=result, down=-10, up=0, avoid_base=False)
    elif (finisher.name == 'OP_LESSTHAN' and correct) or (finisher.name == 'OP_GREATERTHANOREQUAL' and not correct):
        return _random_offset(base_value=result, down=-10, up=-1)
    elif (finisher.name == 'OP_GREATERTHANOREQUAL' and correct) or (finisher.name == 'OP_LESSTHAN' and not correct):
        return _random_offset(base_value=result, down=0, up=10, avoid_base=False)
    else:
        raise ValueError(f'Unknown finisher: {finisher}')

def generate_arithmetic_script(correct: bool)-> list:  # if correct is False, the script should fail the verification
    instructions = []
    stack = []
    strategy = {'reduce': 0, 'keep': 7, 'expand': 14}
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
        except (ValueError, IndexError) as e:
            print(f'W | Operation {operation} not added: {e}')
    result = stack[0]

    if 0 <= result <= 126:  # leaving -1 and 127 as margins for comparisons
        finisher = weighed_choice(_finishers)
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
