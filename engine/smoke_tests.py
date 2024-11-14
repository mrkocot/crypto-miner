from engine.generator import generate_arithmetic_script, generate_tx
from engine import base58

def test_script_generation():
    correct = generate_arithmetic_script(correct=True)
    incorrect = generate_arithmetic_script(correct=False)

    print('Correct:')
    for opc in correct:
        print(f'\t{opc}')
    print('Incorrect:')
    for opc in incorrect:
        print(f'\t{opc}')

def test_base58():
    the_hex = '7d95678e1184400d91d8c79b3181f7e6bd62c688'
    encoded = base58.encode(the_hex)
    decoded = base58.decode_hex(encoded)
    print(f'{the_hex} -> {encoded} -> {decoded}')
    the_int = 476349867049
    encoded = base58.encode(the_int)
    decoded = base58.decode_int(encoded)
    print(f'{the_int} -> {encoded} -> {decoded}')

def test_transaction_generation():
    sources = []
    t = generate_tx(sources)
    print(t)


# test_script_generation()
# test_base58()
# test_transaction_generation()
