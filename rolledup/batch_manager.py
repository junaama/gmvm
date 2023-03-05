class BatchManager:
    def __init__(self, web3, contract_address, batch_size, ABI):
        self.web3 = web3
        self.contract = self.web3.eth.contract(address=contract_address, abi=ABI)
        self.batch_size = batch_size
    
    def submit_batch(self, txs):
        batch = self.web3.eth.batch()
        for tx in txs:
            batch.add(self.contract.functions.execute(*tx))
        tx_hash = batch.execute()
        return tx_hash
