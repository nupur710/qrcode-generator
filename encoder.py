class Encoder:
    def __init__(self):
        self.alphanum= set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./():')

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
        if (encoding=="NUMERIC"):
            return self.numberic_encoding(text)
        elif (encoding=="ALPHANUMERIC"):
            return self.alphanum_encoding(text)
        elif (encoding== "BYTE"):
            return self.byte_encoding(text)
        elif (encoding== "KANJI"):
            return self.kanji_encoding(text)
        

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
            
    def numberic_encoding(self, text):
        print("input data will have numeric encoding")

    def alphanum_encoding(self, text):
        print("intput data will have alphanumeric encoding ")

    def byte_encoding(self, text):
        print("input data will have byte encoding")

    def kanji_encoding(self, text):
        print("input data will have kanji encoding")


t= Encoder()
print(t.encode("日本"))
            
