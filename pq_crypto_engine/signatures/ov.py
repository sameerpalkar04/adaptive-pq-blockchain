import oqs
from pq_crypto_engine.interface import SignatureScheme

class OVScheme(SignatureScheme):
    def __init__(self):
        self.alg = "OV-III"
        # We initialize a signer instance for this specific scheme object
        self.signer = oqs.Signature(self.alg)
        self.public_key = self.signer.generate_keypair()

    def sign(self, message: bytes):
        """Signs a message and returns the signature bytes."""
        return self.signer.sign(message)

    def verify(self, message: bytes, signature, public_key=None):
        """
        Verifies a signature. 
        Research Note: In a real blockchain, we verify using the PK 
        provided in the transaction, not the one stored in the object.
        """
        # If no public_key is provided, fallback to the one owned by this instance
        pk_to_use = public_key if public_key is not None else self.public_key
        
        # We create a stateless verifier for the operation
        with oqs.Signature(self.alg) as verifier:
            # CRITICAL: Return the result so runtime.py gets True/False
            return verifier.verify(message, signature, pk_to_use)

    def get_public_key(self):
        return self.public_key

    def name(self):
        return self.alg