from functools import reduce
from gf_helper import GF
from bitarray import bitarray


class RS:
    def __init__(self):
        self.k = 223
        self.gf = GF(self.k)
        self.n = self.gf.n
        self.int_bitset_mapper = { x: bitarray(f'{x:08b}') for x in range(256) }

    def encode(self, bin_message):
        bitset = bitarray(bin_message)
        pol = bitset.decode(self.int_bitset_mapper)
        enc = []
        parity = (self.n - self.k) * [0]
        for i in range(0, len(pol), self.k - 1):
            enc += self.block_encode(pol[i:i + self.k - 1] + [len(pol[i:i + self.k - 1])] + parity)

        bitset.clear()
        bitset.encode(self.int_bitset_mapper, enc)
        
        return bitset.to01()

    def block_encode(self, block):
        b = self.gf.gf_256_pol_mod(block, self.gf.generator_pol)[1]

        return self.gf.gf_256_pol_subtract(block, b)

    def decode(self, bin_message):
        bitset = bitarray(bin_message)
        pol = bitset.decode(self.int_bitset_mapper)
        dec = []
        for i in range(0, len(pol), self.n):
            dec += self.block_decode(pol[i:i + self.n])

        bitset.clear()
        bitset.encode(self.int_bitset_mapper, dec)
        
        return bitset.to01()

    def block_decode(self, block):
        syndromes = self.syndromes(block)
        corrected = self.correct(block, syndromes)[0]
        _len = corrected.pop()

        return corrected[-_len:]

    def data_parity_split(self, pol):
        partition = -(self.n - self.k)
        data, parity = pol[:partition], pol[partition:]

        return data, parity

    def syndromes(self, pol):
        L = range(self.n - self.k - 1, -1, -1)
        return [self.gf.evaluate(pol, self.gf.gf_256_power(self.gf.g, l + 1)) for l in L] + [0]

    def correct(self, pol, syndromes):
        if all([x == 0 for x in syndromes]):
            return self.data_parity_split(pol)
        else:
            sigma, omega = self.sigma_omega(syndromes)
            X, j = self.error_evaluator(sigma)
            Y = self.forney(omega, X)

        Elist = [0] * self.n
        if len(Y) >= len(j):
            for i in range(self.n):
                if i in j:
                    Elist[i] = Y[j.index(i)]
            E = Elist[::-1]
        else:
            E = []

        c = self.gf.gf_256_pol_subtract(pol, E)
        if self.gf.get_degree(c) > self.gf.get_degree(pol):
            raise Exception("Too many errors.")

        return self.data_parity_split(c)

    def sigma_omega(self, syndromes):
        sigma, old_sigma, omega, old_omega, A, old_A, B, old_B = [1], [1], [1], [1], [0], [0], [1], [1]
        L, old_L, M, old_M = 0, 0, 0, 0
        synd_shift = 0
        pol_multiply, pol_subtract = self.gf.gf_256_pol_multiply, self.gf.gf_256_pol_subtract
        pol_mod, n, k = self.gf.gf_256_pol_mod, self.n, self.k
        if len(syndromes) > (n - k): synd_shift = len(syndromes) - (n - k)
        erasures_count = 0
        for l in range(0, n - k - erasures_count):
            K = erasures_count + l + synd_shift
            Delta = [self.gf.gf_256_pol_multiply(syndromes[:-1] + [1], old_sigma)[-K - 1]]
            sigma = pol_subtract(old_sigma, pol_multiply(pol_multiply(Delta, [1, 0]), old_B))
            omega = pol_subtract(old_omega, pol_multiply(pol_multiply(Delta, [1, 0]), old_A))
            if Delta == [0] or 2 * old_L > K + erasures_count or (2 * old_L == K + erasures_count and old_M == 0):
                A, B, L, M = pol_multiply([1, 0], old_A), pol_multiply([1, 0], old_B), old_L, old_M
            elif (Delta != [0] and 2 * old_L < K + erasures_count) or (2 * old_L == K + erasures_count and old_M != 0):
                A, B, L, M = pol_mod(old_omega, Delta)[0], pol_mod(old_sigma, Delta)[0], K - old_L, 1 - old_M

            old_sigma, old_omega, old_A, old_B = sigma, omega, A, B

        if self.gf.get_degree(omega) > self.gf.get_degree(sigma):
            omega = [omega[-(self.gf.get_degree(sigma) + 1):]]

        omega = pol_mod(pol_multiply(syndromes, sigma), [1] + (n - k + 1) * [0])[1]

        return sigma, omega

    def error_evaluator(self, sigma):
        X, j = [], []
        for l in range(1, self.n + 1):
            if self.gf.evaluate(sigma, self.gf.gf_256_power(self.gf.g, l)) == 0:
                X.append(self.gf.gf_256_power(self.gf.g, -l))
                j.append(self.n - l)
        if len(j) != self.gf.get_degree(sigma):
            raise Exception("Error evaluator check not passed.")

        return X, j

    def forney(self, omega, X):
        E, X_range = [], range(len(X))
        for i in X_range:
            inv = self.gf.gf_256_divide(1, X[i])
            s_tmp = [self.gf.gf_256_subtract(1, self.gf.gf_256_multiply(inv, X[j])) for j in X_range if j != i]
            sigma_prime = reduce(self.gf.gf_256_multiply, s_tmp, 1)
            E.append(self.gf.gf_256_subtract(0, self.gf.gf_256_divide(self.gf.evaluate(omega, inv), sigma_prime)))

        return E
