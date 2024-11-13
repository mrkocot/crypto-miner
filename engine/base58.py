_BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def encode(number: int | str):  # supports numbers in hex strings
    if isinstance(number, str):
        number = int(number, 16)
    encode_result = ''
    while number > 0:
        number, rem = divmod(number, 58)
        encode_result = _BASE58_ALPHABET[rem] + encode_result
    return encode_result


def decode_int(base58) -> int:
    num = 0
    for char in base58:
        num = num * 58 + _BASE58_ALPHABET.index(char)
    return num

def decode_hex(base58) -> str:
    return hex(decode_int(base58))[2:]
