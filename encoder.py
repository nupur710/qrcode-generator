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
            jis_encoded= string.encode('shift_jis')
            print(jis_encoded)
        except UnicodeError:
            return False
        #encoding to shift jis is successfull but we need to make sure the string consists of characters that
        #are in double byte range of shift jis
        byte_arr= bytearray(jis_encoded)
        i= 0
        while i < len(byte_arr):
            if byte_arr[i] >= 0x80: #if current byte is in the first byte range of double-byte characters
                if i+1 < len(byte_arr): #there is another byte
                    first_byte= byte_arr[i]
                    second_byte= byte_arr[i+1]
                    #check first_byte and second_byte are in valid ranges
                    if(0x81 <= first_byte <= 0x9F or 0xE0 <= first_byte <= 0xEF):
                        if((first_byte % 2 != 0 and 0x40 <= second_byte <= 0x9E and second_byte != 0x7f)
                           or (first_byte % 2 == 0 and 0x9F <= second_byte <= 0xFC)):
                            i+= 2 #in range of double-byte character; skip to next pair
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
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
print(t.encode("髜魵魲鮏鮱鮻鰀鵰鵫鶴鸙黑"))
            
