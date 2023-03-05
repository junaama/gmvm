#!/usr/bin/env python3

from typing import Any
from datetime import datetime
import hashlib
import random

class Node:
    def __init__(self, stake=0, address=''):
        self.stake = stake
        self.address = address
    def __iter__(self):
        return iter(self.address)

class Block:
    def __init__(self, timestamp='', prev_hash='', hsh='', validator_addr=''):
        self.timestamp = timestamp
        self.prev_hash = prev_hash
        self.hsh = hsh
        self.validator_addr = validator_addr
    def __iter__(self):
        return iter(self.hsh)

class PosNetwork: 
    def __init__(self, blockchain:list[Block]=[], blockchain_head:Block=Block(), validators:list[Node]=[Node()]):
        self.blockchain = blockchain
        self.blockchain_head = blockchain_head
        self.validators = validators
    
    def __setitem__(self, __key: str, __value: Any) -> None:
        pass
    def __getitem__(self, __key: str) -> Any:
        pass
    def __iter__(self):
        return iter(self.blockchain)
    

n = PosNetwork()

def create_block(_node: Node, n: PosNetwork):
    # penalize node if blockchain has changed
    is_validated = validate_chain(n)
    if is_validated is not None:
        _node.stake -= 10
        return n.blockchain, n.blockchain_head, is_validated
    currentTime = str(datetime.now())
    newBlock = Block(
        timestamp=currentTime,
        prev_hash=n.blockchain_head.hsh,
        hsh=new_block_hash(n.blockchain_head),
        validator_addr=_node.address,
    )
    is_valid_block_candidate = validate_block_candidate(n, newBlock)
    if is_valid_block_candidate is not None:
        _node.stake -= 10
        return n.blockchain, n.blockchain_head, is_valid_block_candidate
    else:
        n.blockchain.append(newBlock)
    
    return n.blockchain, newBlock, None

def new_block_hash(_block: Block) -> str:
    block_info = _block.timestamp + _block.prev_hash + _block.hsh + _block.validator_addr
    return new_hash(block_info)

def new_hash(_data: str) -> str:
    h = hashlib.sha256()
    h.update(_data.encode('utf-8'))
    hashed = h.digest()
    return hashed.hex()

def validate_chain(n: PosNetwork):
    if len(n.blockchain) <= 1:
        return None

    curr_block_idx = len(n.blockchain) - 1
    prev_block_idx = len(n.blockchain) - 2

    while prev_block_idx >= 0:
        curr_block = n.blockchain[curr_block_idx]
        prev_block = n.blockchain[prev_block_idx]
        if curr_block.prev_hash is not prev_block.hsh:
            return "chain has invalid hashes"
        if curr_block.timestamp <= prev_block.timestamp:
            return "chain has invalid timestamps"
        if new_block_hash(prev_block) is not curr_block.hsh:
            return "chain has invalid hash generation"
        curr_block_idx -= 1
        prev_block_idx -= 1
    return None

def validate_block_candidate(n: PosNetwork, _block: Block):
    if n.blockchain_head.hsh is not _block.prev_hash:
        return "blockchain head hash is not equal to new block prev hash"
    if n.blockchain_head.timestamp >= _block.timestamp:
        return "blockchain head timestamp is greater than new block timestamp"
    if new_block_hash(n.blockchain_head) is not _block.hsh:
        return "new block hash is not equal to blockchain head hash"
    return None

def new_node(n: PosNetwork, stake: int):
    new_node = Node(stake=stake, address=random_address())
    n.validators.append(new_node)
    return n.validators

def random_address() -> str:
    b = bytes(random.getrandbits(8) for _ in range(16))
    return ''.join('%02x' % i for i in b)

def select_winner(n: PosNetwork) -> tuple[Node, str]:
    winner_pool= []
    total_stake = 0
    for node in n.validators:
        if node.stake > 0:
            winner_pool.append(node)
            total_stake += node.stake
    if not winner_pool:
        return Node(), "no validators with stake"
    winner_number = int(total_stake)
    temp = 0
    for node in n.validators:
        temp += node.stake
        if temp >= winner_number:
            return node, ""
    return Node(), "no winner found"

def main():
    # set random seed
    random.seed(str(datetime.now()))

    genesis_time = str(datetime.now())
    _blockchain = [Block(timestamp=genesis_time, prev_hash="", hsh=new_hash(genesis_time), validator_addr="")]
    pos = PosNetwork(blockchain=_blockchain, blockchain_head=Block(), validators=[])
    pos.blockchain_head = pos.blockchain[0]
    pos.validators = new_node(pos,60)
    pos.validators = new_node(pos,40)
    for i in range(5):
        winner, err = select_winner(pos)
        if err != "":
            print(err)
            return
        if winner is None:
            print("no winner found")
            return
        winner.stake += 10
        pos_chain, pos_head, err = create_block(winner, pos)
        if err is not None:
            print(err)
            print(pos_chain[0].hsh, pos_head.hsh)
            return
        print("round", i)
        print("address: ", pos.validators[0].address, "-stake", pos.validators[0].stake)
        print("address: ", pos.validators[1].address, "-stake", pos.validators[1].stake)
    
    print("pos info: ", pos)

main()
