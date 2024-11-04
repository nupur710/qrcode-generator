from encoder import Encoder
from versionselector import VersionSelector
from bitarray import bitarray

class ErrorCorrection:
    def __init__(self):
        self.encoder= Encoder()
        self.version= VersionSelector()
        self.gf_exp= [0] * 512 #exponent table
        self.gf_log= [0] * 256 #log table
        self.init_galois_field()
        self.requred_remainder_bits= {
        1: 0, 2: 7, 3: 7, 4: 7, 5: 7,
        6: 7, 7: 0, 8: 0, 9: 0, 10: 0,
        11: 0, 12: 0, 13: 0, 14: 3, 15: 3,
        16: 3, 17: 3, 18: 3, 19: 3, 20: 3,
        21: 4, 22: 4, 23: 4, 24: 4, 25: 4,
        26: 4, 27: 4, 28: 3, 29: 3, 30: 3,
        31: 3, 32: 3, 33: 3, 34: 3, 35: 0,
        36: 0, 37: 0, 38: 0, 39: 0, 40: 0
        }

    #initialize log and exponent table
    def init_galois_field(self):
        primitve_polynomial= 0x11d #285; used for performing xor operations
        x= 1
        for i in range(0, 255):
            self.gf_exp[i]= x
            self.gf_log[x]= i
            x <<= 1
            if(x & 0x100):
                x ^= primitve_polynomial
        for i in range(255, 512):
            self.gf_exp[i]= self.gf_exp[i-255]
    
    def gf_multiply(self, x,y):
        if x== 0 or y== 0: return 0
        return self.gf_exp[self.gf_log[x] + self.gf_log[y] % 255]
    
    def construct_generator_polynomial(self, version):
        num_condewords= self.encoder.block_info[version][1]
        g= [1]
        for i in range(num_condewords):
            g= self.multiply_polynomials(g, [1, self.gf_exp[i]])
        return g

    def multiply_polynomials(self, p1, p2):
        result = [0] * (len(p1) + len(p2) - 1)
        for i in range(len(p1)):
            for j in range(len(p2)):
                result[i + j] ^= self.gf_multiply(p1[i], p2[j])
        return result

    #message polynominal coeffecients
    def message_polynomial(self, text):
        encoded_text= self.encoder.encode(text)
        i= 0
        list= []
        while i < len(encoded_text):
            t= encoded_text[i:i+8]
            i+=8
            list.append(int(t, 2))
        return list
    
    #long division
    def div(self, message_poly, generator_poly):
        remainder = message_poly + [0] * (len(generator_poly) - 1) #padding with len(generator polynomial) - 1 zeros
        for i in range(len(message_poly)):
            if remainder[i] != 0:
                factor = self.gf_log[remainder[i]]
                for j in range(1, len(generator_poly)):
                    if generator_poly[j] != 0:
                        remainder[i + j] ^= self.gf_exp[(factor + self.gf_log[generator_poly[j]]) % 255]
        return remainder[-(len(generator_poly) - 1):]
    
    def split_into_blocks(self, message_poly, version):
        block_info= self.encoder.block_info[version]
        num_blocks1= block_info[2]
        num_blocks2= block_info[3]
        data_codewords1= block_info[4]
        data_codewords2= block_info[5]
        blocks = []
        start = 0
        for i in range(num_blocks1):
            end = start + data_codewords1
            blocks.append(message_poly[start:end])
            start = end
        for i in range(num_blocks2):
            end = start + data_codewords2
            blocks.append(message_poly[start:end])
            start = end
        return blocks
    
    def interleave_blocks(self, data_blocks, ec_blocks):
        interleaved = []
        max_length = max(len(block) for block in data_blocks)
        for i in range(max_length):
            for block in data_blocks:
                if i < len(block):
                    interleaved.append(block[i])
        max_ec_length = len(ec_blocks[0])
        for i in range(max_ec_length):
            for block in ec_blocks:
                interleaved.append(block[i])    
        return interleaved
    
    def get_final_message(self, message, version):
        str= ""
        for num in message:
            str += format(num, '08b')
        remainder_bits_to_add= self.requred_remainder_bits[version]
        for i in range(0, remainder_bits_to_add):
            str += '0'
        return bitarray(str)
        
    
    def generate_error_correction_codewords(self, text, version):
        generator_poly = self.construct_generator_polynomial(version)
        message_poly = self.message_polynomial(text)
        #Split message polynomial into blocks
        data_blocks = self.split_into_blocks(message_poly, version)
        #error correction codewords for each block
        ec_blocks = []
        for block in data_blocks:
            ec_block = self.div(block, generator_poly)
            ec_blocks.append(ec_block)
        #Interleave the data and error correction codewords
        message = self.interleave_blocks(data_blocks, ec_blocks)
        final_message= self.get_final_message(message, version)
        return final_message