class HybridSignature:

    def __init__(self, fast_scheme, strong_scheme):
        self.fast = fast_scheme
        self.strong = strong_scheme

    def sign(self, message):

        sig1 = self.fast.sign(message)
        sig2 = self.strong.sign(message)

        return (sig1, sig2)

    def verify(self, message, signature):

        self.fast.verify(message, signature[0])
        self.strong.verify(message, signature[1])

    def get_public_key(self):
        return (
            self.fast.get_public_key(),
            self.strong.get_public_key()
        )

    def name(self):
        return "HYBRID"