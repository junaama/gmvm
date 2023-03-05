pragma solidity ^0.8.13;
// import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";
import "solady/utils/MerkleProofLib.sol";
contract BatchValidator {
    using MerkleProofLib for bytes32[];

    function validateBatch(
        bytes[] calldata transactions,
        bytes32[] calldata proofs,
        uint256[] calldata indexes
    ) external {
        for (uint256 i = 0; i < transactions.length; i++) {
            bytes32 hash = keccak256(transactions[i]);
            require(verifyProof(hash, proofs[i], indexes[i]), "Invalid proof");

            // Execute the transaction
            (bool success, ) = address(this).call(transactions[i]);
            require(success, "Transaction failed");
        }
    }

    receive() external payable {}

    function verifyProof(
        bytes32 hash,
        bytes32 proof,
        uint256 index
    ) internal pure returns (bool) {
        bytes32 el;
        bytes32 h = hash;

        for (uint256 i = 0; i <= 32; i++) {
            if ((index >> i) & 1 == 1) {
                el = proof;
            } else {
                el = h;
            }

            h = keccak256(abi.encodePacked(h, el));
        }

        return h == proof;
    }
}
