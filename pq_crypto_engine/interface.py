class SignatureScheme:

    def sign(self, message: bytes):
        raise NotImplementedError

    def verify(self, message: bytes, signature):
        raise NotImplementedError

    def get_public_key(self):
        raise NotImplementedError

    def name(self):
        return "BASE_SCHEME"