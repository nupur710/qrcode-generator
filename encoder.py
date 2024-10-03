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
        char_count_indicator= self.get_char_count_indicator(text)
        encoded_data= mode_indicator + char_count_indicator
        if (encoding=="NUMERIC"):
            return encoded_data
        elif (encoding=="ALPHANUMERIC"):
            return encoded_data 
        elif (encoding== "BYTE"):
            return encoded_data 
        elif (encoding== "KANJI"):
            return encoded_data 
        

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

        return format(numchars, f'0{bits}b')


    def numeric_encoding(self, text) :
        list= []
        result= []
        i= 0
        while i < (len(text)):
            t= text[i:i+3]
            i += 3
            list.append(t)
        j= 0
        for group in list:
            binary = bin(int(group))[2:]
            result.append(binary)
        return ''.join(result)
        
            
    # def numberic_encoding(self, text):
    #     print("input data will have numeric encoding")

    # def alphanum_encoding(self, text):
    #     print("intput data will have alphanumeric encoding ")

    # def byte_encoding(self, text):
    #     print("input data will have byte encoding")

    # def kanji_encoding(self, text):
    #     print("input data will have kanji encoding")


t= Encoder()
# print(t.encode("hello world"))
print(t.numeric_encoding('8675309'))

            
