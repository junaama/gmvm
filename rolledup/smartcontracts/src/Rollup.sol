pragma solidity ^0.8.13;

contract Rollup {
    event RollupBlockAppended(uint256 blockNumber, bytes32 root);

    address public sequencer;
    address public validator;

    uint256 public currentBlock;
    mapping(uint256 => bytes32) public blocks;
    mapping(uint256 => bytes32) public blockTransactions;
    mapping(uint256 => bytes32) public blockSignatures;
    mapping(uint256 => bytes32) public blockMerkleRoots;
    mapping(uint256 => address) public sequencerInBlock;

    struct RollupBlock {
        uint256 blockNumber;
        bytes32 root;
        bytes32 transactions;
        bytes32 merkleRoot;
        address sequencer;

    }
    modifier onlySequencer() {
        require(
            msg.sender == sequencer,
            "Only the sequencer can call this function"
        );
        _;
    }
    RollupBlock[] public rollupBlocks;

    function latestRollupBlock() public view returns (RollupBlock memory) {
        require(rollupBlocks.length > 0, "No Rollup Blocks");
        return rollupBlocks[rollupBlocks.length - 1];
    }

    function appendRollupBlock(RollupBlock memory rollupBlock)
        public
        onlySequencer
    {
        require(
            rollupBlock.blockNumber == latestRollupBlock().blockNumber + 1,
            "Invalid block number"
        );
        require(rollupBlock.root != bytes32(0), "Invalid root");
        rollupBlocks.push(rollupBlock);
        emit RollupBlockAppended(rollupBlock.blockNumber, rollupBlock.root);
    }

    constructor(address _sequencer, address _validator) {
        sequencer = _sequencer;
        validator = _validator;

        currentBlock = 0;
        blocks[currentBlock] = bytes32(0);
    }

    function submitBatch(bytes[] memory transactions, bytes[] memory signatures)
        external
    {
        require(
            msg.sender == validator,
            "Only the validator can submit batches"
        );

        bytes32 batchHeader = keccak256(
            abi.encode(transactions, signatures)
        );
        bytes32 prevBlockHash = blocks[currentBlock];

       
        bytes32 blockHash = keccak256(
            abi.encodePacked(batchHeader, prevBlockHash)
        );

        blocks[currentBlock] = blockHash;
         currentBlock++;

    }

    function getRollupBlock(uint256 blockNumber)
        public
        view
        returns (RollupBlock memory)
    {
        require(blockNumber < currentBlock + 1, "Block not yet available");
        RollupBlock memory rollupBlock;
        rollupBlock.transactions = blockTransactions[blockNumber];
        rollupBlock.merkleRoot = blockMerkleRoots[blockNumber];
        rollupBlock.sequencer = sequencerInBlock[blockNumber];
        return rollupBlock;
    }
}
