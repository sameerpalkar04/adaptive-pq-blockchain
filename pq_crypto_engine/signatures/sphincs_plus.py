import oqs
from pq_crypto_engine.interface import SignatureScheme


class SPHINCSScheme(SignatureScheme):
    def __init__(self, variant="SPHINCS+-SHA2-128f-simple"):
        self.alg_name = variant
        self.signer = oqs.Signature(self.alg_name)
        self.public_key = self.signer.generate_keypair()

    def sign(self, message: bytes):
        return self.signer.sign(message)

    def verify(self, message: bytes, signature, public_key=None):
        pk_to_use = public_key if public_key is not None else self.public_key

        with oqs.Signature(self.alg_name) as verifier:
            return verifier.verify(message, signature, pk_to_use)

    def get_public_key(self):
        return self.public_key

    def name(self):
        return self.alg_name