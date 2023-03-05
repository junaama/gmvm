pragma solidity ^0.8.13;

import "./Rollup.sol";
// import "./MerkleProof.sol";
// import "solady/utils/ECSDA.sol";
import "openzeppelin-contracts/contracts/utils/cryptography/ECDSA.sol";
import "openzeppelin-contracts/contracts/utils/cryptography/MerkleProof.sol";
// import "solady/src/utils/MerkleProofLib.sol";

contract Validator {
    Rollup public rollup;
    // Current state of the rollup
    bytes32 public stateRoot;

    // Sequence number of the last batch that was processed
    uint256 public lastBatchSequence;

    constructor(address _rollupAddress) {
        rollup = Rollup(_rollupAddress);
    }

    modifier onlyRollup() {
        require(
            msg.sender == address(rollup),
            "Validator: Only Rollup Contract can call this function"
        );
        _;
    }

    function validateBatch(bytes[] calldata _transactions)
        external
        view
        returns (bool)
    {
        // Validate the batch transactions
        // ...

        // Return true if the batch is valid, false otherwise
        return true;
    }

    function withdrawFees() external {
        // Withdraw the fees
        // ...
    }

    function submitBatch(
        bytes[] calldata transactions,
        bytes32[] calldata proofs
    ) external {
        // Verify that the batch is valid
        require(transactions.length == proofs.length, "Invalid batch");

        // Verify each transaction in the batch
        for (uint256 i = 0; i < transactions.length; i++) {
            bytes32 root = stateRoot;
            bytes32 proof = proofs[i];

            // Verify that the transaction is valid
            require(
                verify(root, proof, transactions[i]),
                "Invalid transaction"
            );

            // Update the state of the rollup
            stateRoot = update(root, transactions[i]);
        }

        // Update the last batch sequence number
        lastBatchSequence++;
    }

    // Verify a transaction using a Merkle proof
    function verify(
        bytes32 root,
        bytes32 proof,
        bytes memory transaction
    ) internal pure returns (bool) {
        return root == keccak256(abi.encodePacked(proof, transaction));
    }

    // Apply a transaction to the current state of the rollup
    function update(bytes32 root, bytes memory transaction)
        internal
        pure
        returns (bytes32)
    {
        return keccak256(abi.encodePacked(root, transaction));
    }

    // Verify the state of the rollup at a given sequence number
    function verifyState(
        uint256 sequence,
        bytes32[] calldata transactions,
        bytes32[] calldata proofs
    ) external view returns (bool) {
        // Verify that the sequence number is valid
        require(sequence <= lastBatchSequence, "Invalid sequence");

        bytes32 root = stateRoot;

        // Verify each transaction in the batch
        for (uint256 i = 0; i < transactions.length; i++) {
            bytes32 proof = proofs[i];

            // Verify that the transaction is valid
            if (i >= sequence) {
                require(
                    verify(root, proof, bytes32(transactions[i])),
                    "Invalid transaction"
                );
            }

            // Update the state of the rollup
            root = update(root, bytes32(transactions[i]));
        }

        // Verify that the state of the rollup matches the expected value
        return root == stateRoot;
    }

    function validateTransaction(
        uint256 txIndex,
        uint256 txBlockNumber,
        bytes memory txProof,
        bytes memory signature
    ) public view returns (bool) {
        Rollup.RollupBlock memory rollupBlock = rollup.getRollupBlock(
            txBlockNumber
        );
        // require(txIndex < rollup.blockTransactions[txIndex].length, "Invalid txIndex");

        bytes32 txHash = keccak256(
            abi.encodePacked(
                keccak256(
                    abi.encodePacked(rollupBlock.transactions[txIndex].sender)
                ),
                keccak256(rollupBlock.transactions[txIndex].data)
            )
        );
        bytes32 merkleRoot = MerkleProof.getMerkleRoot(txProof, txIndex);

        require(merkleRoot == rollupBlock.merkleRoot, "Invalid txProof");

        address recoveredSender = ECDSA.recover(txHash, signature);
        require(recoveredSender == rollupBlock.sequencer, "Invalid signature");

        return true;
    }
}
