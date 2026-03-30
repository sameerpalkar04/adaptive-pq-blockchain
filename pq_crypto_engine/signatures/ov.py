import oqs
from pq_crypto_engine.interface import SignatureScheme


class OVScheme(SignatureScheme):

    def __init__(self):
        self.alg = "OV-III"
        self.signer = oqs.Signature(self.alg)
        self.public_key = self.signer.generate_keypair()

    def sign(self, message: bytes):
        return self.signer.sign(message)

    def verify(self, message: bytes, signature):
        verifier = oqs.Signature(self.alg)
        verifier.verify(message, signature, self.public_key)

    def get_public_key(self):
        return self.public_key

    def name(self):
        return self.alg