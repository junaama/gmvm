pragma solidity ^0.8.13;
import "./Rollup.sol";

contract Sequencer {
    address public rollup;
    uint256 public blockNumber;

    struct Transaction {
        address from;
        address to;
        uint256 amount;
        bytes data;
        uint256 nonce;
    }
    uint256 pendingTxCount;
    mapping(uint256 => Transaction) public transactions;
    mapping(uint256 => Transaction) public pendingTransactions;

    modifier onlyRollup() {
        require(
            msg.sender == rollup,
            "Only the rollup contract can call this function"
        );
        _;
    }

    constructor(address _rollup) {
        rollup = _rollup;
        blockNumber = 0;
    }

    event TransactionSubmitted(
        uint256 indexed blockNumber,
        bytes32 indexed transactionHash,
        uint256 indexed nonce,
        address destination,
        bytes data
    );

    function submitTransaction(
        uint256 nonce,
        address destination,
        bytes calldata data,
        bytes calldata signature
    ) external {
        // Verify the signature is valid
        bytes32 transactionHash = keccak256(
            abi.encode(nonce, destination, data)
        );
        require(
            ecrecover(
                transactionHash,
                uint8(signature[0]),
                bytes32ToBytes(signature, 1),
                bytes32ToBytes(signature, 33)
            ) == rollup,
            "Invalid signature"
        );

        // Verify the nonce is unique
        // require(transactions[nonce], "Nonce already used");
        // require(transactions[nonce] == 0, "Nonce already used");
        transactions[nonce] = Transaction({
            from: msg.sender,
            to: destination,
            amount: 0,
            data: data,
            nonce: nonce
        });

        // Emit an event with the transaction information
        emit TransactionSubmitted(
            blockNumber,
            transactionHash,
            nonce,
            destination,
            data
        );
    }

    event BlockGenerated(
        uint256 indexed blockNumber,
        bytes32 blockHash,
        uint256 timestamp,
        uint256 transactionCount
    );

    function generateBlock() external onlyRollup {
        bytes32[] memory transactionHashes = new bytes32[](
            pendingTxCount
        );
        for (uint256 i = 0; i < pendingTxCount; i++) {
            transactionHashes[i] = keccak256(
                abi.encode(
                    pendingTransactions[i].nonce,
                    pendingTransactions[i].to,
                    pendingTransactions[i].data
                )
            );
        }

        bytes32 blockHash = keccak256(
            abi.encode(blockNumber, transactionHashes)
        );
        uint256 timestamp = block.timestamp;

        emit BlockGenerated(
            blockNumber,
            blockHash,
            timestamp,
            transactionHashes.length
        );

        blockNumber++;
        pendingTxCount = 0;

    }

    function cancelTransaction(uint256 nonce) external onlyRollup {
        delete transactions[nonce];
    }

    function submitTransactions(bytes[] memory _transactions) public {
        (bool succ,) = rollup.call(abi.encodeWithSignature("submitBatch(bytes[])", _transactions));
        require(succ, "submitBatch failed");
    }

    function bytes32ToBytes(bytes memory _bytes, uint256 _start)
        internal
        pure
        returns (bytes32 result)
    {
        require(_bytes.length >= (_start + 32), "bytesToBytes32 out of bounds");
        assembly {
            result := mload(add(_bytes, add(0x20, _start)))
        }
    }
}
