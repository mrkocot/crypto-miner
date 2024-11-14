from engine.structs import Transaction, Block, TxOutput
from engine import generator
from engine.settings import *


class Result:
    def __init__(self, tx: Transaction, accepted: bool):
        self.tx = tx
        self.correct = accepted == (tx.error == 'none')
        self.message = MESSAGES[tx.error]

    def printable(self) -> str:
        correct_str = 'correct' if self.correct else 'incorrect'
        return f'Guess about {self.tx.tx_id} was {correct_str}: {self.message}'

class Game:
    block = Block()
    rejected_tx: list[Transaction] = []
    sources: list[TxOutput] = []
    results: list[Result] = []

    def accept(self, tx: Transaction):
        self.block.transactions.append(tx)
        self.results.append(Result(tx, True))

    def reject(self, tx: Transaction):
        self.rejected_tx.append(tx)
        self.results.append(Result(tx, False))

    def new_tx(self) -> Transaction:
        return generator.generate_tx(self.sources)
