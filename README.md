# Crypto Mine
You are a Bitcoin miner.
Your job is to verify Bitcoin transactions and merge them into a block, which will end up in the famous blockchain.
The whole process is simplified, but resembles what real miners do.

## How to play
To close the block you need to accept at least two transactions.
The goal is to accept all correct ones, and reject every time something is wrong.

### Transaction verification
You can view current transaction with a `tx` command. It will often be correct, but the following errors might occur:
1. Failed script
2. Non-existent input
3. Sum of outputs exceeding sum of inputs
4. Money had already been spent

Every transaction will have an input ID and index. Use `utxo` command to check if it's a valid UTXO.
Perform the following checks:
1. Go through the script and make sure it does not fail
2. UTXO must exist in the database
3. Sum all transaction's outputs - this sum must not be higher than the UTXO value
4. UTXO needs to be marked as `<U>` (unspent). If it's `<S>`, reject the transaction

### Closing the block
After you accept two or more transactions, you need to calculate the `reward`, find the `nonce` and `close` the block.
Nonce will be a number, for which the block's hash starts with two zeroes.
The correct nonce will be found in 128th try on average, but you might be very lucky or not. Just be patient.

## Commands
- `transaction`, `tx` - view current transaction
  - `... new` - get a new transaction
  - `... count`, `... stats` - get statistics of processed transactions so far
- `accept` - mark current transaction as correct
- `reject` - mark current transaction as incorrect
- `utxo <id>` - search Unspent Transaction Outputs database by id
- `reward`, `prize`, `payout` - calculate block reward
- `nonce` - start NONCE lookup
- `close <nonce>`, `end <nonce>` - close the current block (and end the game)

## Simplifications
The game is a simplified version of how miners work. Major differences:

- Miners are racing with each other. When one of them creates a good block, others' work is wasted
- In this game the block's hash needs to start with two zeros. Real blocks need more than 10 (you can try)
- Scripts here have simple arithmetic operations. Real scripts do things like cryptography and hashing
- Real transactions can have multiple inputs, all of them have to be checked
- Real blocks contain more than two transactions (they usually have more or less 3500, you can try that too)
