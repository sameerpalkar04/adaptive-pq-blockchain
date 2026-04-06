import oqs
from pq_crypto_engine.interface import SignatureScheme

class FalconScheme(SignatureScheme):
    def __init__(self):
        self.alg_name = "Falcon-512"
        # Initialize a signer for the instance
        self.signer = oqs.Signature(self.alg_name)
        self.public_key = self.signer.generate_keypair()

    def sign(self, message: bytes):
        """Signs the message using the private key stored in this instance."""
        return self.signer.sign(message)

    def verify(self, message: bytes, signature, public_key=None):
        """
        Verifies a Falcon signature.
        Research-Grade: Supports external public_key for decentralized validation.
        """
        # Fallback to internal key if none provided (useful for local testing)
        pk_to_use = public_key if public_key is not None else self.public_key
        
        # Create a stateless verifier context
        with oqs.Signature(self.alg_name) as verifier:
            # CRITICAL: Return the boolean result to the runtime
            return verifier.verify(message, signature, pk_to_use)

    def get_public_key(self):
        return self.public_key

    def name(self):
        return self.alg_name