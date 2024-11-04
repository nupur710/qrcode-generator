class VersionSelector:
    def __init__(self):
        pass

    #using error correction level M. Max capacity of input chars allowed for numeric, alphanumeric
    #byte, kanji modes for 40 versions of QR codes
    def get_versions_info(self, num_chars, encoding):
        versions_info= {
                1:  [34,  20,  14,  8],
                2:  [63,  38,  26,  16],
                3:  [101, 61,  42,  26],
                4:  [149, 90,  62,  38],
                5:  [202, 122, 84,  52],
                6:  [255, 154, 106, 65],
                7:  [293, 178, 122, 75],
                8:  [365, 221, 152, 93],
                9:  [432, 262, 180, 111],
                10: [513, 311, 213, 131],
                11: [604, 366, 251, 155],
                12: [691, 419, 287, 177],
                13: [796, 483, 331, 204],
                14: [871, 528, 362, 223],
                15: [991, 600, 412, 254],
                16: [1082, 656, 450, 277],
                17: [1212, 734, 504, 310],
                18: [1346, 816, 560, 345],
                19: [1500, 909, 624, 384],
                20: [1600, 970, 666, 410],
                21: [1708, 1035, 711, 438],
                22: [1872, 1134, 779, 480],
                23: [2059, 1248, 857, 528],
                24: [2188, 1326, 911, 561],
                25: [2395, 1451, 997, 614],
                26: [2544, 1542, 1059, 652],
                27: [2701, 1637, 1125, 692],
                28: [2857, 1732, 1190, 732],
                29: [3035, 1839, 1264, 778],
                30: [3289, 1994, 1370, 843],
                31: [3486, 2113, 1452, 894],
                32: [3693, 2238, 1538, 947],
                33: [3909, 2369, 1628, 1002],
                34: [4134, 2506, 1722, 1060],
                35: [4343, 2632, 1809, 1113],
                36: [4588, 2780, 1911, 1176],
                37: [4775, 2894, 1989, 1224],
                38: [5039, 3054, 2099, 1292],
                39: [5313, 3220, 2213, 1362],
                40: [5596, 3391, 2331, 1435]
            }
        for k,v in versions_info.items():
            if v[encoding] >= num_chars:
                return k
        return None

    def smallest_version(self, text, encoding_mode):
        version= None
        num_chars= len(text)
        if encoding_mode== 'NUMERIC': version= self.get_versions_info(num_chars, 0)
        elif encoding_mode== 'ALPHANUMERIC': version= self.get_versions_info(num_chars, 1)
        elif encoding_mode== 'BYTE': version= self.get_versions_info(num_chars, 2)
        elif encoding_mode== 'KANJI': version= self.get_versions_info(num_chars, 3)    
        else: raise ValueError("Input is too long for available versions")
        return version