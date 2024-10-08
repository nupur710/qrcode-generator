from BitArray2D import BitArray2D
import numpy as np
from versionselector import VersionSelector
from encoder import Encoder
from errorcorrection import ErrorCorrection
from PIL import Image

class QRCodeGenerator3b:
    def __init__(self):
        self.version_selector= VersionSelector()
        self.alignment_pattern_locations= {
            2:  [6, 18],
            3:  [6, 22],
            4:  [6, 26],
            5:  [6, 30],
            6:  [6, 34],
            7:  [6, 22, 38],
            8:  [6, 24, 42],
            9:  [6, 26, 46],
            10: [6, 28, 50],
            11: [6, 30, 54],
            12: [6, 32, 58],
            13: [6, 34, 62],
            14: [6, 26, 46, 66],
            15: [6, 26, 48, 70],
            16: [6, 26, 50, 74],
            17: [6, 30, 54, 78],
            18: [6, 30, 56, 82],
            19: [6, 30, 58, 86],
            20: [6, 34, 62, 90],
            21: [6, 28, 50, 72, 94],
            22: [6, 26, 50, 74, 98],
            23: [6, 30, 54, 78, 102],
            24: [6, 28, 54, 80, 106],
            25: [6, 32, 58, 84, 110],
            26: [6, 30, 58, 86, 114],
            27: [6, 34, 62, 90, 118],
            28: [6, 26, 50, 74, 98, 122],
            29: [6, 30, 54, 78, 102, 126],
            30: [6, 26, 52, 78, 104, 130],
            31: [6, 30, 56, 82, 108, 134],
            32: [6, 34, 60, 86, 112, 138],
            33: [6, 30, 58, 86, 114, 142],
            34: [6, 34, 62, 90, 118, 146],
            35: [6, 30, 54, 78, 102, 126, 150],
            36: [6, 24, 50, 76, 102, 128, 154],
            37: [6, 28, 54, 80, 106, 132, 158],
            38: [6, 32, 58, 84, 110, 136, 162],
            39: [6, 26, 54, 82, 110, 138, 166],
            40: [6, 30, 58, 86, 114, 142, 170]
        }

    def generate(self, text):
        encoder= Encoder()
        error_correction= ErrorCorrection()
        encoding_mode= encoder.determine_encoding(text)
        version= self.version_selector.smallest_version(text, encoding_mode)
        final_message= error_correction.generate_error_correction_codewords(text)
        qr_size= 21 + (version-1) * 4 #arithmetic progression
        #qr_matrix= BitArray2D(rows= qr_size, columns= qr_size)
        qr_matrix = np.zeros((qr_size, qr_size), dtype=int)
        self.place_finder_patterns2(qr_matrix)
        self.place_alignment_patterns(qr_matrix, version)
        self.place_timing_pattern(qr_matrix)
        self.place_dark_module(qr_matrix, version)
        self.place_data(qr_matrix, final_message, version)
        masked_matrix, best_mask= self.apply_best_mask(qr_matrix, version)
        format_string= self.generate_format_string(best_mask)
        self.place_format_information(masked_matrix, format_string)
        version_info= self.generate_version_information(version)
        self.place_version_information(masked_matrix, version_info)
        final_qr= self.add_quiet_zone(masked_matrix)
        self.export_to_png(final_qr, "my_qr.png")
        print(final_qr)
        return final_qr
        

    # def place_finder_patterns(self, qr_matrix):
    #     finder_pattern_data = [
    #     [1, 1, 1, 1, 1, 1, 1],
    #     [1, 0, 0, 0, 0, 0, 1],
    #     [1, 0, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 0, 1],
    #     [1, 0, 1, 1, 1, 0, 1],
    #     [1, 0, 0, 0, 0, 0, 1],
    #     [1, 1, 1, 1, 1, 1, 1]
    # ]
    #     finder_pattern=  BitArray2D(rows= 7, columns= 7)
    #     for i in range(7):
    #         for j in range(7):
        
    #             finder_pattern[i,j]= finder_pattern_data[i][j]
    #     print("here")
    #     print(finder_pattern)  
    #     print("****")     
    #     print(finder_pattern_data)
    #     return finder_pattern

    def place_finder_patterns2(self, qr_matrix):
        finder_pattern = np.array([
            [1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]
        ])

        qr_matrix[0:7, 0:7] = finder_pattern
        qr_matrix[0:7, -7:] = finder_pattern
        qr_matrix[-7:, 0:7] = finder_pattern

    def place_alignment_patterns(self, qr_matrix, version):
        if version == 1:
            return

        locations = self.alignment_pattern_locations[version]
        size = qr_matrix.shape[0]

        for row in locations:
            for col in locations:
                # Check if the alignment pattern overlaps with finder patterns or separators
                if not self.overlaps_finder_pattern(row, col, size):
                    self.place_single_alignment_pattern(qr_matrix, row, col)

    def overlaps_finder_pattern(self, row, col, size):
        # Check top-left, top-right, and bottom-left corners
        return ((row < 8 and col < 8) or
                (row < 8 and col > size - 9) or
                (row > size - 9 and col < 8))

    def place_single_alignment_pattern(self, qr_matrix, center_row, center_col):
        for i in range(-2, 3):
            for j in range(-2, 3):
                if abs(i) == 2 or abs(j) == 2 or (i == 0 and j == 0):
                    qr_matrix[center_row + i, center_col + j] = 1
                else:
                    qr_matrix[center_row + i, center_col + j] = 0

    

    def place_timing_pattern(self, qr_matrix):
        size = qr_matrix.shape[0]
        for i in range(8, size - 8):
            self.set_bit(qr_matrix, 6, i, i % 2 == 0)
            self.set_bit(qr_matrix, i, 6, i % 2 == 0)
        print("here")

    def place_dark_module(self, qr_matrix, version):
        self.set_bit(qr_matrix, (4*version)+9, 8, 1)

    def set_bit(self, qr_matrix, row, col, value):
        qr_matrix[row, col] = value

    def place_data(self, qr_matrix, final_message, version):
        size = qr_matrix.shape[0]
        up = True
        data_index = 0
        
        for right in range(size - 1, 0, -2):
            if right == 7:  # skip vertical timing pattern
                right -= 1
            
            for vertical in range(size - 1, -1, -1) if up else range(size):
                for left in range(right, right - 2, -1):
                    if left < 0:
                        continue
                    
                    if self.is_data_module(qr_matrix, vertical, left, version):
                        self.set_bit(qr_matrix, vertical, left, final_message[data_index])
                        data_index += 1
                        if data_index >= len(final_message):
                            return
            
            up = not up

    def is_data_module(self, qr_matrix, row, col, version):
        size = qr_matrix.shape[0]
        
        #Check if module overlaps with finder pattern
        if (row < 9 and col < 9) or (row < 9 and col > size - 9) or (row > size - 9 and col < 9):
            return False
        
        # Check if module overlaps with horizontal timing pattern
        if row == 6:
            return False
        
        # Check if module overlaps vertical timing pattern
        if col == 6:
            return False
        
        # Check if module is in an alignment pattern
        if size > 21:  # alignment pattern is only ofr versions >= 2
            alignment_positions = self.get_alignment_pattern_positions(version)
            for pos_x in alignment_positions:
                for pos_y in alignment_positions:
                    if (pos_x - 2 <= row <= pos_x + 2) and (pos_y - 2 <= col <= pos_y + 2):
                        return False
        
        # Check if module is the dark module
        if row == 4 * version + 9 and col == 8:
            return False
        
        #data module
        return True

    def get_alignment_pattern_positions(self, version):
        if version == 1:
            return []
        return self.alignment_pattern_locations[version]
    
    def apply_best_mask(self, qr_matrix, version):
        best_mask = 0
        best_score = float('inf')
        
        for mask in range(8):
            masked_matrix = self.apply_mask(qr_matrix, mask, version)
            score = self.evaluate_mask(masked_matrix)
            if score < best_score:
                best_score = score
                best_mask = mask
        
        return self.apply_mask(qr_matrix, best_mask, version), best_mask
    
    def apply_mask(self, qr_matrix, mask_pattern, version):
        size = qr_matrix.shape[0]
        masked_matrix = qr_matrix.copy()
        
        for row in range(size):
            for col in range(size):
                if self.is_data_module(masked_matrix, row, col, version):
                    if self.mask_function(mask_pattern, row, col):
                        masked_matrix[row, col] = 1 - masked_matrix[row, col]  # Toggle the bit
        
        return masked_matrix

    def mask_function(self, mask_pattern, row, col):
        if mask_pattern == 0:
            return (row + col) % 2 == 0
        elif mask_pattern == 1:
            return row % 2 == 0
        elif mask_pattern == 2:
            return col % 3 == 0
        elif mask_pattern == 3:
            return (row + col) % 3 == 0
        elif mask_pattern == 4:
            return (row // 2 + col // 3) % 2 == 0
        elif mask_pattern == 5:
            return ((row * col) % 2) + ((row * col) % 3) == 0
        elif mask_pattern == 6:
            return (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
        elif mask_pattern == 7:
            return (((row + col) % 2) + ((row * col) % 3)) % 2 == 0

    def evaluate_mask(self, masked_matrix):
        return (self.evaluate_condition_1(masked_matrix) +
                self.evaluate_condition_2(masked_matrix) +
                self.evaluate_condition_3(masked_matrix) +
                self.evaluate_condition_4(masked_matrix))

    def evaluate_condition_1(self, matrix):
        penalty = 0
        size = matrix.shape[0]
        for row in range(size):
            count = 1
            for col in range(1, size):
                if matrix[row, col] == matrix[row, col-1]:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
            if count >= 5:
                penalty += 3 + (count - 5)
        for col in range(size):
            count = 1
            for row in range(1, size):
                if matrix[row, col] == matrix[row-1, col]:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
            if count >= 5:
                penalty += 3 + (count - 5)

        return penalty

    def evaluate_condition_2(self, matrix):
        penalty = 0
        size = matrix.shape[0]

        for row in range(size - 1):
            for col in range(size - 1):
                if (matrix[row, col] == matrix[row, col+1] == 
                    matrix[row+1, col] == matrix[row+1, col+1]):
                    penalty += 3

        return penalty

    def evaluate_condition_3(self, matrix):
        penalty = 0
        size = matrix.shape[0]
        pattern1 = np.array([1, 0, 1, 1, 1, 0, 1])
        pattern2 = np.array([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0])
        for row in range(size):
            for col in range(size - 6):
                if np.array_equal(matrix[row, col:col+7], pattern1):
                    if col >= 4 and np.all(matrix[row, col-4:col] == 0):
                        penalty += 40
                    elif col + 11 <= size and np.all(matrix[row, col+7:col+11] == 0):
                        penalty += 40
        for col in range(size):
            for row in range(size - 6):
                if np.array_equal(matrix[row:row+7, col], pattern1):
                    if row >= 4 and np.all(matrix[row-4:row, col] == 0):
                        penalty += 40
                    elif row + 11 <= size and np.all(matrix[row+7:row+11, col] == 0):
                        penalty += 40

        return penalty

    def evaluate_condition_4(self, matrix):
        total_modules = matrix.size
        dark_modules = np.sum(matrix)
        dark_percentage = (dark_modules / total_modules) * 100

        prev_multiple = (dark_percentage // 5) * 5
        next_multiple = prev_multiple + 5

        prev_deviation = abs(prev_multiple - 50) // 5
        next_deviation = abs(next_multiple - 50) // 5

        return min(prev_deviation, next_deviation) * 10
    
    def generate_format_string(self, mask_pattern):
        ec_indicator = '00'
        mask_indicator = f'{mask_pattern:03b}'
        format_bits = ec_indicator + mask_indicator
        generator_poly = int('10100110111', 2)
        format_poly = int(format_bits + '0' * 10, 2)
        
        for _ in range(5):
            if format_poly.bit_length() >= generator_poly.bit_length():
                format_poly ^= generator_poly << (format_poly.bit_length() - generator_poly.bit_length())
        
        error_correction_bits = f'{format_poly:010b}'
        format_string = format_bits + error_correction_bits
        
        # xor with mask
        mask = int('101010000010010', 2)
        final_format = int(format_string, 2) ^ mask
        
        return f'{final_format:015b}'
    
    def place_format_information(self, qr_matrix, format_string):
        size = qr_matrix.shape[0]
        
        for i in range(6):
            qr_matrix[8, i] = int(format_string[i])
            qr_matrix[i, 8] = int(format_string[14 - i])
        qr_matrix[7, 8] = int(format_string[6])
        qr_matrix[8, 7] = int(format_string[7])
        qr_matrix[8, 8] = int(format_string[8])
        
        for i in range(8):
            qr_matrix[size - 1 - i, 8] = int(format_string[i])
        for i in range(7):
            qr_matrix[8, size - 7 + i] = int(format_string[14 - i])

    def generate_version_information(self, version):
        if version < 7:
            return None
        
        version_indicator = f'{version:06b}'
        version_poly = int(version_indicator + '000000000000', 2)
        generator_poly = int('1111100100101', 2)
        
        for _ in range(6):
            if version_poly.bit_length() >= generator_poly.bit_length():
                version_poly ^= generator_poly << (version_poly.bit_length() - generator_poly.bit_length())
        
        error_correction_bits = f'{version_poly:012b}'
        return version_indicator + error_correction_bits
    
    def place_version_information(self, qr_matrix, version_info):
        if version_info is None:
            return
        
        size = qr_matrix.shape[0]
        
        for i in range(6):
            for j in range(3):
                qr_matrix[size - 11 + j, i] = int(version_info[i * 3 + j])

        for i in range(6):
            for j in range(3):
                qr_matrix[i, size - 11 + j] = int(version_info[i * 3 + j])

    def place_dark_module(self, qr_matrix, version):
        qr_matrix[4 * version + 9, 8] = 1

    def add_quiet_zone(self, qr_matrix):
        size = qr_matrix.shape[0]
        new_size = size + 8
        new_matrix = np.zeros((new_size, new_size), dtype=int)
        new_matrix[4:-4, 4:-4] = qr_matrix
        return new_matrix
    
    def export_to_png(self, qr_matrix, filename, scale=10, quiet_zone=True):
        if quiet_zone:
            qr_matrix = self.add_quiet_zone(qr_matrix)
        
        height, width = qr_matrix.shape
        image = Image.new('RGB', (width * scale, height * scale), 'white')
        pixels = image.load()

        for y in range(height):
            for x in range(width):
                if qr_matrix[y, x] == 1:
                    for i in range(scale):
                        for j in range(scale):
                            pixels[x * scale + i, y * scale + j] = (0, 0, 0)

        image.save(filename)
        print(f"QR code saved as {filename}")

    
        
q= QRCodeGenerator3b()
q.generate("Congratulations-Challenge-Complete")
