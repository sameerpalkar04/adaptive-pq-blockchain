// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PQRegistry {
    struct TransactionRecord {
        string txHash;
        string scheme;
        string threat;
        uint256 latency;
        bool verified;
        uint256 timestamp;
    }

    TransactionRecord[] public records;

    function logTransaction(
        string memory _txHash,
        string memory _scheme,
        string memory _threat,
        uint256 _latency,
        bool _verified
    ) public {
        records.push(
            TransactionRecord(
                _txHash,
                _scheme,
                _threat,
                _latency,
                _verified,
                block.timestamp
            )
        );
    }

    function getCount() public view returns (uint256) {
        return records.length;
    }

    function getRecord(uint256 index)
        public
        view
        returns (
            string memory,
            string memory,
            string memory,
            uint256,
            bool,
            uint256
        )
    {
        TransactionRecord memory record = records[index];
        return (
            record.txHash,
            record.scheme,
            record.threat,
            record.latency,
            record.verified,
            record.timestamp
        );
    }
}