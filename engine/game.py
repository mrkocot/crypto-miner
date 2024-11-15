from engine.structs import Transaction, Block, TxOutput
from engine import generator
from engine.settings import *


class Result:
    def __init__(self, tx: Transaction, accepted: bool):
        self.tx = tx
        self.accepted = accepted
        self.correct = accepted == (tx.error == 'none')
        self.message = MESSAGES[tx.error]

    def printable(self) -> str:
        wrongly = 'rightfully' if self.correct else 'WRONGFULLY'
        decision = 'accepted' if self.accepted else 'rejected'
        return f'Transaction {self.tx.tx_id}: {wrongly} {decision} - {self.message}'

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

    def source_lookup(self, tx_id: str) -> list[TxOutput]:
        res = filter(lambda src: src.tx_id == tx_id, self.sources)
        return sorted(res, key=lambda src: src.index)

    def result_summary(self) -> dict:  # True = correct
        res = {True: 0, False: 0}
        for r in self.results:
            res[r.correct] += 1
        return res
