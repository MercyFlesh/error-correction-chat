class GF:
    def __init__(self, k = 223):
        self.n = 255
        self.irreducible = 0x1b
        self.g = 3
        self.gf_256_tables()
        self.generator_pol = self.get_generator(k)

    def get_degree(self, a):
        if a[0] != 0:
            return len(a) - 1
        else:
            for i in range(1, len(a)):
                if a[i] != 0: return len(a) - i - 1
            return 0

    def get_generator(self, k):
        g = [1]
        for i in range(self.n - k):
            p = [1, self.gf_256_power(self.g, i + 1)]
            g = self.gf_256_pol_multiply(g, p)

        return g

    def evaluate(self, a, x):
        res = a[-1]
        for _pow, _coef in enumerate(range(len(a) - 2, -1, -1), 1):
            res = self.gf_256_sum(res, self.gf_256_multiply(a[_coef], self.gf_256_power(x, _pow)))

        return res

    def mul_operation(self, a, b):
        p = 0
        for _ in range(8):
            if a == 0 or b == 0: break
            if b & 1:
                p ^= a
            b = b >> 1
            carry = a & 0x80
            a = (a << 1) & 0xFF
            if carry:
                a ^= self.irreducible

        return p

    def gf_256_tables(self):
        self.log_table = (self.n + 1) * [0]
        self.antilog_table = self.n * [0]
        x = 1
        for i in range(self.n):
            self.log_table[x] = i
            self.antilog_table[i] = x
            x = self.mul_operation(x, self.g)

    def gf_256_sum(self, a, b):
        return a ^ b

    def gf_256_subtract(self, a, b):
        return self.gf_256_sum(a, b)

    def gf_256_multiply(self, a, b):
        if (a == 0) or (b == 0): 
            return 0
        
        x = self.log_table[a]
        y = self.log_table[b]
        log_mult = (x + y) % self.n

        return self.antilog_table[log_mult]

    def gf_256_divide(self, a, b):
        if (a == 0) or (b == 0): 
            return 0
        
        x = self.log_table[a]
        y = self.log_table[b]
        log_mult = (x - y) % self.n

        return self.antilog_table[log_mult]

    def gf_256_power(self, a, n):
        x = self.log_table[a]
        z = (x * n) % self.n

        return self.antilog_table[z]

    def gf_256_pol_sum(self, a, b):
        pad = (max(len(a), len(b)) - min(len(a), len(b))) * [0]
        if len(a) > len(b):
            b = pad + b
        elif len(b) > len(a):
            a = pad + a

        return [a[i] ^ b[i] for i in range(len(a))]

    def gf_256_pol_subtract(self, a, b):
        return self.gf_256_pol_sum(a, b)

    def gf_256_pol_multiply(self, a, b):
        res = [0] * (len(a) + len(b) - 1)
        for o1, i1 in enumerate(a):
            for o2, i2 in enumerate(b):
                mul = self.gf_256_multiply(i1, i2)
                res[o1 + o2] = self.gf_256_sum(res[o1 + o2], mul)

        return res

    def gf_256_pol_divide(self, a, b):
        return self.gf_256_pol_mod(a, b)[0]

    def gf_256_pol_power(self, a, n):
        b = a[:]
        for _ in range(n - 1):
            a = self.gf_256_pol_multiply(a, b)

        return a

    def gf_256_pol_mod(self, a, b):
        a_degree, b_degree = self.get_degree(a), self.get_degree(b)
        a_coeff, b_coeff = a[-(a_degree + 1)], b[-(b_degree + 1)]
        if b_degree < 0:
            raise ZeroDivisionError
        elif a_degree < b_degree:
            quotient, remainder = [0], a
        else:
            quotient, remainder = (a_degree + 1) * [0], a
            quotient_degree, remainder_degree, = a_degree - b_degree, a_degree
            remainder_coeff = a_coeff
            while quotient_degree >= 0 and not all([x == 0 for x in remainder]):
                quotient_coeff = self.gf_256_divide(remainder_coeff, b_coeff)
                q = [quotient_coeff] + [0] * quotient_degree
                quotient[-(quotient_degree + 1)] = quotient_coeff
                remainder = self.gf_256_pol_subtract(remainder, self.gf_256_pol_multiply(q, b))
                remainder_degree = self.get_degree(remainder)
                remainder_coeff = remainder[-(remainder_degree + 1)]
                quotient_degree = remainder_degree - b_degree

        return quotient, remainder