pragma solidity ^0.8.13;

contract BatchedTransaction {
    address public rollupAddress;
    address[] public recipients;
    uint256[] public amounts;

    constructor(address _rollupAddress) {
        rollupAddress = _rollupAddress;
    }

    //
    function addTransaction(address recipient, uint256 amount) public {
        require(
            msg.sender == tx.origin,
            "only externally owned accounts allowed"
        );

        recipients.push(recipient);
        amounts.push(amount);
    }

    function submitBatch() public {
        require(recipients.length > 0, "no transactions to batch");

        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }

        for (uint256 i = 0; i < recipients.length; i++) {
            (bool success, ) = rollupAddress.call{value: amounts[i]}(
                abi.encodeWithSignature(
                    "transfer(address,uint256)",
                    recipients[i],
                    amounts[i]
                )
            );
            require(success, "batched transfer failed");
        }

        recipients = new address[](0);
        amounts = new uint256[](0);

        emit BatchSubmitted(totalAmount);
    }

    event BatchSubmitted(uint256 totalAmount);
}
