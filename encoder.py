from versionselector import VersionSelector

class Encoder:
    def __init__(self):
        self.version= VersionSelector()
        self.alphanum= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./():')
        self.mode_indicators= {
            "NUMERIC": "0001",
            "ALPHANUMERIC": "0010",
            "BYTE": "0100",
            "KANJI": "1000"
        }

        self.alphanumeric_values = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17, "I": 18,
    "J": 19, "K": 20, "L": 21, "M": 22, "N": 23, "O": 24, "P": 25, "Q": 26, "R": 27,
    "S": 28, "T": 29, "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34, "Z": 35, " ": 36,
    "$": 37, "%": 38, "*": 39, "+": 40, "-": 41, ".": 42, "/": 43, ":": 44
}
        #0th index: total codewords
        #1st index: error correcting codewords per block
        #2nd index: no. of blocks of 1st type
        #3rd index: no. of blocks of 2nd type
        #4th index: data codewords per block of 1st type
        #5th index: data codewords per block of 2nd type
        self.block_info= {
    1: [16, 10, 1, 0, 16, 0], 
    2: [28, 16, 1, 0, 28, 0], 
    3: [44, 26, 1, 0, 44, 0], 
    4: [64, 18, 2, 0, 32, 0], 
    5: [86, 24, 2, 0, 43, 0],
    6: [108, 16, 4, 0, 27, 0], 
    7: [124, 18, 4, 0, 31, 0], 
    8: [154, 22, 2, 2, 38, 39], 
    9: [182, 22, 3, 2, 36, 37], 
    10: [216, 22, 4, 1, 43, 44],
    11: [254, 30, 1, 4, 50, 51], 
    12: [290, 22, 6, 2, 36, 37], 
    13: [334, 22, 8, 1, 37, 38],
    14: [365, 24, 4, 5, 40, 41], 
    15: [415, 24, 5, 5, 41, 42],
    16: [453, 28, 7, 3, 45, 46], 
    17: [507, 28, 10, 1, 46, 47], 
    18: [563, 26, 9, 4, 43, 44], 
    19: [627, 26, 3, 11, 44, 45], 
    20: [669, 26, 3, 13, 41, 42],
    21: [714, 26, 17, 0, 42, 0], 
    22: [782, 28, 17, 0, 46, 0], 
    23: [860, 28, 4, 5, 121, 122], 
    24: [914, 2, 6, 14, 45, 46], 
    25: [1000, 28, 8, 13, 47, 48],
    26: [1062, 28, 19, 4, 46, 47], 
    27: [1128, 28, 22, 3, 45, 46], 
    28: [1193, 28, 3, 23, 45, 46], 
    29: [1267, 28, 21, 7, 45, 46], 
    30: [1373, 28, 19, 10, 47, 48],
    31: [1455, 28, 2, 29, 46, 47], 
    32: [1541, 28, 10, 23, 46, 47], 
    33: [1631, 28, 14, 21, 46, 47], 
    34: [1725, 28, 14, 23, 46, 47], 
    35: [1812, 28, 12, 26, 47, 48],
    36: [1914, 28, 6, 34, 47, 48], 
    37: [1992, 28, 29, 14, 46, 47], 
    38: [2102, 28, 13, 32, 46, 47], 
    39: [2216,  28, 40, 7, 47, 48], 
    40: [2334, 28, 18, 31, 47, 48]
    }

        


    def determine_encoding(self, text):
        isByteEncode= self.is_iso8859_1(text)
        isDoubleByteJIS= self.is_doubleByteJIS(text)
        if(text.isnumeric()):
            return "NUMERIC"
        elif all(char in self.alphanum for char in text):
            return "ALPHANUMERIC"
        elif isByteEncode:
            return "BYTE"
        elif isDoubleByteJIS:
            return "KANJI"
        else:
            return "BYTE"
        

    def encode(self, text):
        encoding= self.determine_encoding(text)
        mode_indicator= self.mode_indicators[encoding]
        char_count_indicator, version= self.get_char_count_indicator(text)
        encoded_data= mode_indicator + char_count_indicator + self.__get_encoded_data__(encoding, text)
        padding_1= self.terminator_padding(version, encoded_data)
        padding_2= self.pad_to_multiples_of_8(padding_1)
        padding_fin= self.add_236_and_17(padding_2, version)
        return padding_fin
        # if (encoding=="NUMERIC"):
        #     return encoded_data
        # elif (encoding=="ALPHANUMERIC"):
        #     return encoded_data 
        # elif (encoding== "BYTE"):
        #     return encoded_data 
        # elif (encoding== "KANJI"):
        #     return encoded_data 
        

    def is_iso8859_1(self, string):
        try:
            #during encoding, if char is not found in  in ISO8859-1 character table, throw Unicode Error
            string.encode('latin-1')
            return True
        except UnicodeError:
            return False
        
    #encode string in shift jist & then determine byte ranges
    def is_doubleByteJIS(self, string):
        try:
            jis_encoded = string.encode('shift_jis')
        except UnicodeEncodeError:
            return False
        if len(jis_encoded) % 2 != 0:  # if odd no. of bytes, not double-byte character
            return False
        for i in range(0, len(jis_encoded), 2):
            first_byte = jis_encoded[i]
            second_byte = jis_encoded[i+1]
            if not ((0x81 <= first_byte <= 0x9F or 0xE0 <= first_byte <= 0xFC) and
                (0x40 <= second_byte <= 0x7E or 0x80 <= second_byte <= 0xFC)):
                return False
        return True
    
        
    def get_char_count_indicator(self, text):
        numchars= len(text)
        encoding_mode= self.determine_encoding(text)
        version= self.version.smallest_version(text, encoding_mode)
        bits= None
        if encoding_mode== "NUMERIC":
            if version <= 9:
                bits= 10
            elif 10 <= version <= 26:
                bits= 12
            elif 27 <= version <= 40:
                bits= 14
        elif encoding_mode== "ALPHANUMERIC":
            if version <= 9:
                bits= 9
            elif 10 <= version <= 26:
                bits= 11
            elif 27 <= version <= 40:
                bits= 13
        elif encoding_mode== "BYTE":
            if version <= 9:
                bits= 8
            else:
                bits= 16
        elif encoding_mode== "KANJI":
            if version <= 9:
                bits= 8
            elif 10 <= version <= 26:
                bits= 10
            elif 27 <= version <= 40:
                bits= 12

        return format(numchars, f'0{bits}b'), version
    
    def __get_encoded_data__(self, encoding, text):
        if encoding== "NUMERIC": return self.numeric_encoding(text)
        elif encoding== "ALPHANUMERIC": return self.alphanumeric_encoding(text)
        elif encoding== "BYTE": return self.byte_encoding(text)
        elif encoding== "KANJI": return self.kanji_encoding(text)

    def terminator_padding(self, version, encoded_data):
        current_bits= len(encoded_data)
        total_bits= self.block_info[version][0] * 8
        remainig_bits= total_bits - current_bits
        if remainig_bits >= 4:
            encoded_data+= '0000'
        else:
            encoded_data += '0' * remainig_bits
        return encoded_data
    
    def pad_to_multiples_of_8(self, encoded_data):
        while(len(encoded_data) % 8 != 0):
            encoded_data += '0'
        return encoded_data
    
    def add_236_and_17(self, encoded_data, version):
        total_bits= self.block_info[version][0] * 8
        pad_236= '11101100'
        pad_17= '00010001'
        pad_flag= True
        while (len(encoded_data) < total_bits):
            if pad_flag:
                encoded_data+= pad_236
            else:
                encoded_data+= pad_17
            pad_flag= not pad_flag
        return encoded_data

    def numeric_encoding(self, text) :
        list= []
        result= []
        i= 0
        while i < (len(text)):
            t= text[i:i+3]
            i += 3
            list.append(t)
        for group in list:
            binary = bin(int(group))[2:]
            result.append(binary)
        return ''.join(result)
    
    def alphanumeric_encoding(self, text):
        list= []
        i= 0
        result= ""
        while i < (len(text)):
            t= text[i:i+2]
            i+= 2
            list.append(t)
        for group in list:
            if len(group)== 2:
                c1= group[0]
                c2= group[1]
                sum= (self.alphanumeric_values[c1] * 45) + self.alphanumeric_values[c2]
                b= format(sum, '011b')
            else:
                c = group[0]
                sum = self.alphanumeric_values[c]
                b = format(sum, '06b')
            result += b
        return result
    
    def byte_encoding(self, text):
        try:
            byte_encoded= text.encode('iso-8859-1')
        except UnicodeError:
            byte_encoded= text.encode('utf-8')

        binary_str= ""
        for byte in byte_encoded:
            binary_str += format(byte, '08b')
        return binary_str
    
    def kanji_encoding(self, text):
        kanji_encoded= text.encode('shift_jis')
        result= ""
        for i in range(0, len(kanji_encoded), 2):
            byte = (kanji_encoded[i] << 8) | kanji_encoded[i + 1]
            if 0x8140 <= byte <= 0x9FFC:
                h= byte - 0x8140
                res= (((h>>8) & 0xFF) * 0xC0)  + (h & 0xFF) #msb= (h>>8) & 0xFF; lsb= h & 0xFF 
                res_b= format(res, '013b')
            elif 0xE040 <= byte <= 0xEBBF:
                h= byte - 0xC140
                res= (((h>>8) & 0xFF) * 0xC0)  + (h & 0xFF)
                res_b= format(res, '013b')
            result += res_b
        return result
