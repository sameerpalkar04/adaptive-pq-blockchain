import oqs
from pq_crypto_engine.interface import SignatureScheme

class DilithiumScheme(SignatureScheme):
    def __init__(self, level="5"):
        # Mapping level to OQS algorithm name
        self.alg_name = f"Dilithium{level}"
        self.signer = oqs.Signature(self.alg_name)
        self.public_key = self.signer.generate_keypair()

    def sign(self, message: bytes):
        """Signs the message using the Dilithium private key."""
        return self.signer.sign(message)

    def verify(self, message: bytes, signature, public_key=None):
        """
        Verifies a Dilithium signature.
        Complexity: Accepts dynamic public keys for blockchain state validation.
        """
        pk_to_use = public_key if public_key is not None else self.public_key
        
        with oqs.Signature(self.alg_name) as verifier:
            # Return result of lattice-based verification
            return verifier.verify(message, signature, pk_to_use)

    def get_public_key(self):
        return self.public_key

    def name(self):
        return self.alg_name