from encoder import Encoder
from versionselector import VersionSelector

class ErrorCorrection:
    def __init__(self):
        self.encoder= Encoder()
        self.version= VersionSelector()
        #error correcting codewords per block
        self.m_ec_codewords= {
    1: 10, 2: 16, 3: 26, 4: 18, 5: 24,
    6: 16, 7: 18, 8: 22, 9: 22, 10: 26,
    11: 30, 12: 22, 13: 22, 14: 24, 15: 24,
    16: 28, 17: 28, 18: 26, 19: 26, 20: 26,
    21: 26, 22: 28, 23: 28, 24: 28, 25: 28,
    26: 28, 27: 28, 28: 28, 29: 28, 30: 28,
    31: 28, 32: 28, 33: 28, 34: 28, 35: 28,
    36: 28, 37: 28, 38: 28, 39: 28, 40: 28
    }
        self.gf_exp= [0] * 512 #exponent table
        self.gf_log= [0] * 256 #log table
        self.init_galois_field()

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
        num_condewords= self.m_ec_codewords[version]
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
    
    def generate_error_correction_codewords(self, text):
        encoding_mode= self.encoder.determine_encoding(text)
        version= self.version.smallest_version(text, encoding_mode)
        generator_poly = self.construct_generator_polynomial(version)
        message_poly = self.message_polynomial(text)
        error_correction_codewords = self.div(message_poly, generator_poly)
        
        return error_correction_codewords

    
e= ErrorCorrection()
e.generate_error_correction_codewords("HELLO WORLD")