import itertools


class Convolutional:
    def __init__(self):
        self.gen = Convolutional._gnrs((5, 7, 27, 111, 230, 34, 52, 66, 89, 103, 153, 255))
        self.K = len(max(self.gen, key=len)) - 1
        self.regi = [0] * self.K

    def gen_op(self, s):
        shift = self.regi
        res = ""
        for i in range(len(s)):
            shift.insert(0, s[i])
            for fun in self.gen:
                xor_bits = [shift[i] for i, s in enumerate(fun[::-1]) if s == '1']
                res += str(Convolutional._xor(*xor_bits))
            shift.pop()
            
        return res

    def encode(self, bin_mesage):
        input_enc = []
        for s in bin_mesage:
            input_enc += [int(k) for k in s]
            
        return self.gen_op(input_enc + [0] * self.K)

    def decode(self, data):
        register = self.regi.copy()
        f_bits = ''.join(str(e) for e in data)
        F_bits = [f_bits[i:i + len(self.gen)] for i in range(0, len(f_bits), len(self.gen))]
        Vit_dict_keys = [''.join(map(str, i)) for i in itertools.product([0, 1], repeat=self.K)]
        Vit_dict = {i: [] for i in Vit_dict_keys}
        turn = 0
        while turn < len(F_bits):
            if turn == 0:
                prev = "".join(str(i) for i in register)
                op_1 = self.one_bit_change(register, 0)
                op_1_d = Convolutional._hamming_distance(F_bits[turn], op_1)
                Vit_dict[f'0{prev[1:]}'] = [f"{prev} -> 0{prev[:self.K - 1]}"] + [op_1_d]
                op_2 = self.one_bit_change(register, 1)
                op_2_d = Convolutional._hamming_distance(F_bits[turn], op_2)
                Vit_dict[f'1{prev[1:]}'] = [f"{prev} -> 1{prev[:self.K - 1]}"] + [op_2_d]
            else:
                temp_trails = []
                for path in Vit_dict.values():
                    if path:
                        register = [int(i) for i in path[-2][-self.K:]]
                        prev = "".join(str(i) for i in register)
                        op_1 = self.one_bit_change(register, 0)
                        op_1_d = Convolutional._hamming_distance(F_bits[turn], op_1)
                        new_path1 = path + [f"{prev} -> 0{prev[:self.K - 1]}", path[-1] + op_1_d]
                        temp_trails.append(new_path1)
                        op_2 = self.one_bit_change(register, 1)
                        op_2_d = Convolutional._hamming_distance(F_bits[turn], op_2)
                        new_path2 = path + [f"{prev} -> 1{prev[:self.K - 1]}", path[-1] + op_2_d]
                        temp_trails.append(new_path2)
                        
                find_path = sorted(temp_trails, key=lambda x: x[-2][-self.K:])
                for i, best_path in enumerate(find_path):
                    try:
                        if best_path[-2][-self.K:] == find_path[i + 1][-2][-self.K:]:
                            want = min(best_path[-1], find_path[i + 1][-1])
                            if want == best_path[-1]:
                                find_path.remove(find_path[i + 1])
                                pass
                            else:
                                best_path = find_path[i + 1]
                                find_path.remove(best_path)
                                Vit_dict[best_path[-2][-self.K:]] = best_path
                                continue
                    except IndexError:
                        pass
                    
                    Vit_dict[best_path[-2][-self.K:]] = best_path   
            turn += 1
            
        win_order = []
        try:
            win_order = sorted(Vit_dict.items(), key=lambda x: x[-1][-1])
        except IndexError:
            for i in Vit_dict.items():
                if i:
                    win_order.append(i)
                    
            win_order = sorted(win_order, key=lambda x: x[-1][-1])
            
        winner = next(iter(win_order))
        trans = [i[:self.K] for i in winner[1] if type(i) == str]
        final = []
        for index, item in enumerate(trans):
            try:
                a = f'1{item[:-1]}'
                if f'1{item[:-1]}' == trans[index + 1]:
                    final.append(1)
                else:
                    final.append(0)
            except IndexError:
                pass
            
        del final[-self.K + 1:]
        return ''.join(str(e) for e in final)

    def one_bit_change(self, shift_list, num_in):
        shift = shift_list.copy()
        data = []
        shift.insert(0, num_in)
        for fun in self.gen:
            xor_bits = [shift[i] for i, s in enumerate(fun[::-1]) if s == '1']
            data.append(Convolutional._xor(*xor_bits))
            
        return ''.join(str(i) for i in data)
    
    @staticmethod
    def _xor(*kwargs):
        sum = 0
        for num in kwargs:
            sum += num
            
        return int(1 == sum % 2)

    @staticmethod
    def _hamming_distance(s1, s2):
        return sum(s1[i] != s2[i] for i in range(len(s1)))

    @staticmethod
    def _gnrs(gnr):
        k = [bin(i).replace('0b', '') for i in gnr]
        s = max(k, key=len)
        for i, b in enumerate(k[:]):
            if len(b) < len(s):
                b = '0' * (len(s) - len(b)) + b
                k.insert(i, b)
                k.pop(i + 1)
                
        return k