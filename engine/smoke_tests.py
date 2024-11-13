from engine.generator import generate_arithmetic_script

correct = generate_arithmetic_script(correct=True)
incorrect = generate_arithmetic_script(correct=False)

print('Correct:')
for opc in correct:
    print(f'\t{opc}')
print('Incorrect:')
for opc in incorrect:
    print(f'\t{opc}')
