// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PQRegistry {
    struct TransactionRecord {
        string txHash;
        string scheme; // e.g., "ECDSA", "DILITHIUM5", "FALCON"
        string threat;
        uint256 latency;
        bool verified;
        uint256 timestamp;
    }

    TransactionRecord[] public records;

    // Mapping to simulate known public keys for specific schemes
    // In a real PQC system, these would be the OQS-compatible public keys
    mapping(string => bytes) public registeredPublicKeys;

    event SecurityAlert(string reason, string schemeUsed);
    event TransactionLogged(
        string txHash, 
        string scheme, 
        string threat, 
        uint256 latency, 
        bool verified
    );

    /**
     * @dev Enhanced logTransaction that simulates verification logic.
     * For Simulation 1: If scheme is "ECDSA", it passes easily (vulnerable).
     * For Simulation 2: If middleware sets "DILITHIUM5", it requires complex verification.
     */
    function logAndVerify(
        string memory _txHash,
        string memory _scheme,
        string memory _threat,
        uint256 _latency,
        bytes memory _signature // Pass the actual signature here for the simulation
    ) public returns (bool) {

        bool isVerified = false;
    
        // SIMULATION LOGIC:
        // Case 1: Legacy ECC (Simulation 1 scenario)
        if (keccak256(abi.encodePacked(_scheme)) == keccak256(abi.encodePacked("ECDSA"))) {
            // We simulate a successful ECC check even if forged, 
            // representing the "Quantum Break" where the key is compromised.
            isVerified = true; 
        } 
        // Case 2: PQC Enforcement (Simulation 2 scenario)
        else if (keccak256(abi.encodePacked(_scheme)) == keccak256(abi.encodePacked("DILITHIUM5"))) {
            // Here, we check if the signature length matches a valid Dilithium signature.
            // A "forged" classical signature will fail this check.
            if (_signature.length >= 2420) { // Approx size for Dilithium5 sig
                isVerified = true;
            } else {
                emit SecurityAlert("PQC Verification Failed: Signature Mismatch", _scheme);
                isVerified = false;
            }
        }

        records.push(
            TransactionRecord(
                _txHash,
                _scheme,
                _threat,
                _latency,
                isVerified,
                block.timestamp
            )
        );

        emit TransactionLogged(_txHash, _scheme, _threat, _latency, isVerified);
        return isVerified;
    }

    function getCount() public view returns (uint256) {
        return records.length;
    }

    function getRecord(uint256 index) public view returns (
        string memory txHash,
        string memory scheme,
        string memory threat,
        uint256 latency,
        bool verified,
        uint256 timestamp
    ) {
        TransactionRecord memory r = records[index];
        return (r.txHash, r.scheme, r.threat, r.latency, r.verified, r.timestamp);
    }
}