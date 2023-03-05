from web3 import Web3, HTTPProvider
from eth_account import Account
from typing import List
from web3.middleware import geth_poa_middleware
from eth_account import Account
from typing import List
from rollup_block import RollupBlock
import time
import json 
from datetime import datetime

class Sequencer:
    def __init__(self, node_url: str, private_key: str, gas_price: int, block_time, rollup_contract, chain):
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.account = Account.privateKeyToAccount(private_key)
        self.gas_price = gas_price
        self.web3 = Web3(HTTPProvider(node_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = Account.from_key(private_key)
        self.contract = self.web3.eth.contract(address="ROLLUP_CONTRACT_ADDRESS", abi=ROLLUP_CONTRACT_ABI)
        self.block_time = block_time
        self.transaction_queue = []
        self.rollup_contract = rollup_contract
        self.chain = chain 
        self.ethereum = Ethereum(node_url)
        self.account = Account.from_key(private_key)
        self.block_number = self.ethereum.get_block_number()
        self.transactions = []
        self.max_txns_per_batch = 1000
        self.private_key = private_key

    def get_next_block(self) -> RollupBlock:
        # Get latest Ethereum block
        latest_block = self.web3.eth.getBlock('latest')

        # TODO: Construct a new RollupBlock with transactions waiting in mempool
        block = RollupBlock()

        # Sign the block with sequencer's private key
        signed_block = self.account.sign_message(block.hash())

        # Return the signed block
        return signed_block

    def submit_block(self, block: RollupBlock) -> str:
        # Submit the block to the rollup contract
        tx_hash = self.contract.functions.commitBlock(block).transact({'from': self.account.address, 'gas': 1000000})

        # Return the transaction hash
        return tx_hash.hex()

    def add_transaction(self, tx):
        self.transaction_queue.append(tx)
        self.transactions.append(tx)

    
    def create_block(self):
        if len(self.transaction_queue) == 0:
            return

        transactions = self.transaction_queue[:]
        self.transaction_queue.clear()

        block_data = {"transactions": transactions}

        signed_block = self.web3.eth.account.sign_message(block_data, self.account.privateKey)
        block_hash = self.web3.eth.send_raw_transaction(signed_block.rawTransaction)

        time.sleep(self.block_time)
        self.create_block()
    
    def get_unprocessed_txs(self):
        unprocessed_txs = self.rollup_contract.get_unprocessed_txs()
        return unprocessed_txs

    def process_txs(self, txs):
        txs.sort(key=lambda x: x['nonce'])
        signed_txs = []
        for tx in txs:
            unsigned_tx = {
                'nonce': tx['nonce'],
                'gasPrice': self.chain.eth.gas_price,
                'gas': tx['gas'],
                'to': tx['to'],
                'value': tx['value'],
                'data': tx['data']
            }
            signed_tx = Account.sign_transaction(unsigned_tx, self.private_key)
            signed_txs.append(signed_tx)
        return signed_txs

    def submit_batch(self, signed_txs, block):
        self.rollup_contract.submit_batch(signed_txs)
        if block is None:
            return None
        encoded_block = json.dumps(block.to_dict())
        tx_hash = self.ethereum.send_transaction(self.account, '', encoded_block)
        return tx_hash
    
    def create_batch(self):
        if len(self.transactions) == 0:
            return None
        elif len(self.transactions) > self.max_txns_per_batch:
            transactions = self.transactions[:self.max_txns_per_batch]
            self.transactions = self.transactions[self.max_txns_per_batch:]
        else:
            transactions = self.transactions
            self.transactions = []
        block_number = self.block_number + 1
        self.block_number = block_number
        block = RollupBlock(block_number, transactions, )
        return block
        nonce = self.get_next_nonce()
        # batch = []
        # for tx in transactions:
        #     tx['nonce'] = nonce
        #     batch.append(tx)
        #     nonce += 1
        # return batch

    def send_batch(self, batch):
        tx = self.web3.eth.account.signTransaction({
            'nonce': self.get_next_nonce(),
            'gasPrice': self.web3.eth.gas_price,
            'gas': 1000000,
            'data': b'',
            'to': self.web3.eth.accounts[0],
            'value': 0,
            'chainId': self.web3.eth.chainId,
            'txType': 2,
            'accessList': [],
            'maxPriorityFeePerGas': self.web3.eth.gas_price,
            'maxFeePerGas': self.web3.eth.gas_price * 2,
            'batch': batch
        }, self.private_key)
        return self.web3.eth.send_raw_transaction(tx.rawTransaction)

    def get_rollup_block(self):
        return self.web3.eth.get_block('latest')

    def get_next_nonce(self) -> int:
        return self.web3.eth.getTransactionCount(self.account.address)

    def sign_transaction(self, transaction: dict) -> dict:
        signed = self.account.sign_transaction(transaction)
        return signed.rawTransaction

    def send_signed_transactions(self, signed_transactions: List[dict]) -> List[str]:
        tx_hashes = []
        for signed_tx in signed_transactions:
            tx_hash = self.web3.eth.sendRawTransaction(signed_tx)
            tx_hashes.append(tx_hash.hex())
        return tx_hashes

    def get_balance(self) -> int:
        return self.web3.eth.getBalance(self.account.address)

if __name__ == "__main__":
    web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    account = web3.eth.account.create("")
    time_now = datetime.now()
    contract_address = ""
    chain = ""
    sequencer = Sequencer(web3, account, 10, time_now, contract_address, chain)

    while True:
        tx = input("Enter transaction: ")
        sequencer.add_transaction(tx)
