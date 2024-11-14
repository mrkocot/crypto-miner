REQUIRED_TX = 8
MESSAGES = {
    'none': 'This transaction is correct',
    'script_failed': 'In this transaction, script verification should fail',
    'negative_fee': 'In this transaction, sum of outputs is larger that sum of inputs',
    'invalid_input': 'This transaction uses non-existent funds',
    'already_spent': 'This transaction uses funds which had already been spent',
}