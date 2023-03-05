from web3 import Web3 
from eth_abi import encode_abi

class Batcher:
    def __init__(self, node_url, contract_address, private_key):
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.contract_address = contract_address
        self.private_key = private_key

    def encode_transaction(self, to, value, data):
        nonce = self.web3.eth.getTransactionCount(self.web3.eth.accounts[0])
        gas_price = self.web3.eth.gasPrice
        gas_limit = 1000000
        tx_data = {
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'to': to,
            'value': value,
            'data': data,
        }
        signed_tx = self.web3.eth.account.signTransaction(tx_data, self.private_key)
        return signed_tx.rawTransaction

    def batch_transactions(self, transactions):
        to_addresses = []
        values = []
        data = []
        for tx in transactions:
            to_addresses.append(tx['to'])
            values.append(tx['value'])
            data.append(tx['data'])
        encoded_data = encode_abi(['address[]', 'uint256[]', 'bytes[]'], [to_addresses, values, data])
        encoded_data_hex = encoded_data.hex()
        tx_data = self.encode_transaction(self.contract_address, 0, encoded_data_hex)
        tx_hash = self.web3.eth.sendRawTransaction(tx_data)
        return tx_hash


if __name__ == '__main__':
    node_url = 'http://localhost:8545'
    contract_address = ''
    private_key = ''
    batcher = Batcher(node_url, contract_address, private_key=private_key)
    # mock raw transactions
    transactions = [
        {
            'to': '',
            'value': 1000000000000000000,
            'data': '0x',
        },
        {
            'to': '',
            'value': 1000000000000000000,
            'data': '0x',
        },
        {
            'to': '',
            'value': 1000000000000000000,
            'data': '0x',
        },
    ]
    tx_hash = batcher.batch_transactions(transactions)
    print(tx_hash.hex())



