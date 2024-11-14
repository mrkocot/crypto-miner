import inspect

class OpCode:
    def __init__(self, number: int, name: str, body):
        self.number = number
        self.name = name
        self.body = body

    def apply(self, stack: list):
        argnum = len(inspect.signature(self.body).parameters)
        if len(stack) < argnum:
            raise IndexError('Not enough elements on the stack')
        if argnum == 0:
            ret = self.body()
        else:
            args = stack[-argnum:]
            del stack[-argnum:]
            ret = self.body(*args)
        if ret is not None:
            if type(ret) is list or type(ret) is tuple:
                stack.extend(ret)
            else:
                stack.append(ret)

    def to_hex(self) -> str:
        return f'{self.number:02x}'

    def __str__(self) -> str:
        return self.name

class OpPushBytes(OpCode):
    def __init__(self, hex_bytes: str):
        if len(hex_bytes) % 2 != 0:
            hex_bytes = '0' + hex_bytes
        byte_number = len(hex_bytes) // 2
        dec = int(hex_bytes, 16)
        if byte_number > 75:
            raise ValueError('Trying to push more than 75 bytes')
        self.hex_bytes = hex_bytes
        lambda_result = dec if byte_number <= 4 else hex_bytes
        super().__init__(byte_number, f'OP_PUSHBYTES{byte_number}', lambda : lambda_result)

    def to_hex(self):
        super().to_hex() + self.hex_bytes

    def __str__(self) -> str:
        return self.name + ':' + self.hex_bytes

class OpX(OpCode):
    def __init__(self, number: int):
        if number > 16:
            raise ValueError('Trying to push number over 16 directly')
        elif number < -1:
            raise ValueError('Trying to push negative number (not -1) directly')
        elif number == -1:
            super().__init__(79, 'OP_1NEGATE', lambda: -1)
        elif number == 0:
            super().__init__(0, f'OP_0', lambda: 0)
        else:
            super().__init__(80 + number, f'OP_{number}', lambda: number)


class TxIO:  # transaction input or output
    def __init__(self, tx_id: str, index: int, script: list):
        self.tx_id = tx_id
        self.index = index
        self.script = script  # "chest lock" in case of outputs, "chest key" in case of inputs

class TxInput(TxIO):
    pass

class TxOutput(TxIO):
    def __init__(self, tx_id: str, index: int, script: list, amount: int):
        self.amount = amount
        super().__init__(tx_id, index, script)


class Transaction:
    def __init__(self, tx_id: str, input_: TxInput, outputs: list[TxOutput], total: int, fee: int, error: str):
        self.tx_id = tx_id
        self.input = input_
        self.outputs = outputs
        self.total = total
        self.fee = fee
        self.error = error
