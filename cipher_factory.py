from bitarray import bitarray


class CipherFactory:
    @staticmethod
    def encode(alg_class, message, mistake='0'):
        bin_message = CipherFactory._str_to_bin(message)
        alg = alg_class()
        encoded_message = alg.encode(bin_message)
        
        return CipherFactory._make_mistake_in_encoded_message(encoded_message, mistake)
    
    @staticmethod
    def decode(alg_class, bin_message):
        alg = alg_class()
        decoded = alg.decode(bin_message)
        
        return CipherFactory._bin_to_str(decoded)
    
    @staticmethod
    def _str_to_bin(message):
        bitset = bitarray()
        bitset.frombytes(message.encode('utf-8'))
        
        return bitset.to01()

    @staticmethod
    def _bin_to_str(bin_message):
        bin_message = bin_message[bin_message.find('1'):]
        bin_message = '0' * (8 - len(bin_message) % 8 if len(bin_message) % 8 != 0 else 0) + bin_message
        bitset = bitarray(bin_message)
        
        return bitset.tobytes().decode('utf-8')
    
    @staticmethod
    def _make_mistake_in_encoded_message(message, mistake='0'):
        if mistake == '0':
            return message
        try:
            bin_mistake = format(int(mistake), 'b').zfill(len(message))
        except ValueError:
            return message
        res_list = [str(ord(a) ^ ord(b)) for a, b in zip(message, bin_mistake)]
        
        return ''.join(res_list)
