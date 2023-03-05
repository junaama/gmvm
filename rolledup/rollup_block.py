class RollupBlock:
    def __init__(self, number, previous_block_hash, state_root, tx_root, timestamp, contract_address, transactions):
        self.number = number
        self.previous_block_hash = previous_block_hash
        self.state_root = state_root
        self.tx_root = tx_root
        self.timestamp = timestamp
        self.contract_address = contract_address
        self.transactions = transactions
