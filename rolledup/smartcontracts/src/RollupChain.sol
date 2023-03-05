pragma solidity ^0.8.13;

contract RollupChain {
    struct Transaction {
        address from;
        address to;
        uint256 amount;
        bytes data;
        uint256 nonce;
    }

    mapping(uint256 => Transaction) public transactions;
    uint256 public currentBlockNumber;

    function submitTransaction(
        address _from,
        address _to,
        uint256 _amount,
        uint256 _nonce,
        bytes calldata _data
    ) public {
        transactions[currentBlockNumber] = Transaction(_from, _to, _amount, _data, _nonce);
        currentBlockNumber++;
        Transaction memory transaction = Transaction(_from, _to, _amount, _data, _nonce);
        transactions[_nonce] = transaction;
    }

    function processTransactions(
        uint256[] calldata nonces,
        address[] calldata tos,
        uint256[] calldata values,
        bytes[] calldata datas
    ) external {
        require(
            nonces.length == tos.length &&
                tos.length == values.length &&
                values.length == datas.length,
            "Invalid input lengths"
        );

        for (uint256 i = 0; i < nonces.length; i++) {
            Transaction memory transaction = transactions[nonces[i]];

            // verify transaction details
            require(transaction.to == tos[i], "Invalid transaction details");
            require(
                transaction.amount == values[i],
                "Invalid transaction details"
            );
            require(
                keccak256(transaction.data) == keccak256(datas[i]),
                "Invalid transaction details"
            );

            // execute transaction
            (bool success, ) = transaction.to.call{value: transaction.amount}(
                transaction.data
            );
            require(success, "Transaction failed");

            // remove transaction from mapping
            delete transactions[nonces[i]];
        }
    }
}
