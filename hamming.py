from math import log2


class Hamming:
    GENERATING_MATRIX_LEN = 1024

    def __init__(self):
        # self._generating_matrix_filename = 'generating_matrix.txt'
        # self.generating_matrix = self._generate_matrix()
        self.generating_matrix = [0] + [0 if log2(i + 1) - int(log2(i + 1)) == 0 else None for i in
                                        range(1, self.GENERATING_MATRIX_LEN)]
        self.hamming_message_len = None

    def _fill_generating_matrix(self, message):
        gen_index = 2
        msg_index = 0
        while msg_index < len(message):
            if self.generating_matrix[gen_index] is None:
                self.generating_matrix[gen_index] = int(message[msg_index])
                msg_index += 1
            gen_index += 1
        self.hamming_message_len = gen_index

    def encode(self, bin_message):
        self._fill_generating_matrix(bin_message)

        check = 1
        while check <= self.hamming_message_len:
            lst = []
            for i in range(check - 1, self.hamming_message_len, 2 * check):
                line = map(lambda x: 0 if not x else x, self.generating_matrix[i:i + check])
                lst.extend(line)
            counter = sum(lst)
            self.generating_matrix[check - 1] = 1 if counter % 2 else 0
            check *= 2

        return ''.join(map(str, self.generating_matrix[:self.hamming_message_len]))

    def decode(self, message):
        msg_without_control_bits = ''
        check_bits = []
        for i in range(2, len(message)):
            if log2(i + 1) - int(log2(i + 1)) != 0:
                msg_without_control_bits = ''.join((msg_without_control_bits, message[i]))
            else:
                check_bits.append(message[i])
        encoded = self.encode(msg_without_control_bits)

        fixed_message = self._fix_errors(message, encoded)
        bin_result = Hamming._delete_control_bits(fixed_message)
        
        return ''.join(bin_result)

    def _fix_errors(self, original, encoded):
        error_bits = []
        i = 1
        while i < self.hamming_message_len:
            if original[i - 1] != encoded[i - 1]:
                error_bits.append(i)
            i *= 2

        error_bits_sum_index = sum(error_bits) - 1
        if error_bits:
            new_bit = '1' if original[error_bits_sum_index] == '0' else '0'
        else:
            return original

        return ''.join((encoded[:error_bits_sum_index], new_bit, encoded[error_bits_sum_index + 1:]))

    @staticmethod
    def _delete_control_bits(datalist):
        res = []

        for i in range(2, len(datalist)):
            if log2(i + 1) - int(log2(i + 1)) != 0:
                res.append(datalist[i])

        return res
