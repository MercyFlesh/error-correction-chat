import numpy as np
from pyldpc import make_ldpc, decode, get_message, encode


class LDPC:
    def __init__(self):
        self.n = 20
        self.d_v = 4
        self.d_c = 5
        self.snr = 10

        self.H, self.G = make_ldpc(self.n, self.d_v, self.d_c, systematic=True, sparse=True)
        _, self.k = self.G.shape
    
    def encode(self, bin_message):
        bin_message = '0' * (self.k - len(bin_message) % self.k if len(bin_message) % self.k != 0 else 0) + bin_message
        encoded = ""
        for i in range(0, len(bin_message), self.k):
            v = np.fromiter(bin_message[i: i + self.k], dtype=np.int32)
            y = encode(self.G, v, self.snr)
            d = decode(self.H, y, self.snr, maxiter=100)
            encoded += ''.join(str(num) for num in d)
            
        return encoded
    
    def decode(self, encoded_message):
        decoded = ""
        for i in range(0, len(encoded_message), self.n):
            x = get_message(self.G, np.fromiter(encoded_message[i: i + self.n], dtype=np.int32))
            decoded += ''.join(str(num) for num in x)
            
        return decoded
