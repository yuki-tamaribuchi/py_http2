import struct

from ..utils.flags import is_flagged
from ..utils.bin import bin_padding
from ..utils.huffman import decode

class Field:
	FIELD_TYPES = {
		"0": "Indexed Header Field",
		"1": "Literal Header Field with Incremental Indexing -- Indexed Name",
		"2": "Literal Header Field with Incremental Indexing -- New Name",
		"3": "Literal Header Field without Indexing -- Indexed Name",
		"4": "Literal Header Field without Indexing -- New Name",
		"5": "Literal Header Field Never Indexed -- Indexed Name",
		"6": "Literal Header Field Never Indexed -- New Name",
		"7": "Maximum Dynamic Table Size Change"
	}
	STATIC_HUFFMAN_TABLE = {
		" ": "010100",
		"!": "1111111000",
		"\"": "1111111001",
		"#": "111111111010",
		"$": "1111111111001",
		"%": "010101",
		"&": "11111000",
		"'": "11111111010",
		"(": "1111111010",
		")": "1111111011",
		"*": "11111001",
		"+": "11111111011",
		",": "11111010",
		"-": "010110",
		".": "010111",
		"/": "011000",
		"0": "00000",
		"1": "00001",
		"2": "00010",
		"3": "011001",
		"4": "011010",
		"5": "011011",
		"6": "011100",
		"7": "011101",
		"8": "011110",
		"9": "011111",
		":": "1011100",
		";": "11111011",
		"<": "111111111111100",
		"=": "100000",
		">": "111111111011",
		"?": "1111111100",
		"@": "1111111111010",
		"A": "100001",
		"B": "1011101",
		"C": "1011110",
		"D": "1011111",
		"E": "1100000",
		"F": "1100001",
		"G": "1100010",
		"H": "1100011",
		"I": "1100100",
		"J": "1100101",
		"K": "1100110",
		"L": "1100111",
		"M": "1101000",
		"N": "1101001",
		"O": "1101010",
		"P": "1101011",
		"Q": "1101100",
		"R": "1101101",
		"S": "1101110",
		"T": "1101111",
		"U": "1110000",
		"V": "1110001",
		"W": "1110010",
		"X": "11111100",
		"Y": "1110011",
		"Z": "11111101",
		"[": "1111111111011",
		"\\": "1111111111111110000",
		"]": "1111111111100",
		"^": "11111111111100",
		"_": "100010",
		"`": "111111111111101",
		"a": "00011",
		"b": "100011",
		"c": "00100",
		"d": "100100",
		"e": "00101",
		"f": "100101",
		"g": "100110",
		"h": "100111",
		"i": "00110",
		"j": "1110100",
		"k": "1110101",
		"l": "101000",
		"m": "101001",
		"n": "101010",
		"o": "00111",
		"p": "101011",
		"q": "1110110",
		"r": "101100",
		"s": "01000",
		"t": "01001",
		"u": "101101",
		"v": "1110111",
		"w": "1111000",
		"x": "1111001",
		"y": "1111010",
		"z": "1111011",
		"{": "111111111111110",
		"|": "11111111100",
		"}": "11111111111101",
		"~": "1111111111101"
	}
	STATIC_HUFFMAN_REVERSE_TABLE = {v:k for k, v in STATIC_HUFFMAN_TABLE.items()}

	def __init__(self, field_type:int, index=None, name=None, name_h=None, value=None, value_h=None, max_size=None):
		if index == 0:
			print("Index must be 1 or over")

		self.field_type = field_type
		self.field_type_str = self.FIELD_TYPES[str(self.field_type)]

		if self.field_type in [0, 1, 3, 5]:
			if index is None:
				print("Please specify index")
				raise Exception
			self.index = index

		if self.field_type in [2, 4, 6]:
			if name is None:
				print("Please specify name")
				raise Exception
			if name_h is None:
				print("Please specify name_h")
				raise Exception
			self.name = name
			self.name_h = name_h
		
		if self.field_type in [1, 2, 3, 4, 5, 6]:
			if value is None:
				print("Please specify value")
				raise Exception
			if value_h is None:
				print("Please specify value_h")
				raise Exception
			self.value = value
			self.value_h = value_h
		
		if self.field_type == 7:
			if max_size is None:
				print("Please specify max_size")
				raise Exception
	
	@classmethod
	def load_raw_frame(self, raw_frame):
		def load_next_field(raw_frame):
			return Field.load_raw_frame(raw_frame)

		def is_all_flagged(bits):
			for b in bits:
				if not b == 1:
					return False
			return True

		def load_name(raw_frame):
			current_byte_idx = 0
			h_and_name_length_bin = bin_padding(bin(raw_frame[0]).replace("0b", ""))
			name_h = bool(int(h_and_name_length_bin[0]))
			if is_all_flagged(h_and_name_length_bin[1:]):
				name_length, current_byte_idx = calc_multi_byte_value(raw_frame[1:], len(h_and_name_length_bin[1:]))
			else:
				name_length = int(h_and_name_length_bin[1:], 2)
			name = raw_frame[1:1+name_length]
			return (name, name_h, name_length, current_byte_idx)

		def load_value(raw_frame):
			current_byte_idx = 0
			h_and_value_length_bin = bin_padding(bin(raw_frame[0]).replace("0b", ""))
			value_h = bool(int(h_and_value_length_bin[0]))
			if is_all_flagged(h_and_value_length_bin[1:]):
				value_length, current_byte_idx = calc_multi_byte_value(raw_frame[1:], len(h_and_value_length_bin[1:]))
			else:
				value_length = int(h_and_value_length_bin[1:], 2)
			value = raw_frame[1:1+value_length]
			return (value, value_h, value_length, current_byte_idx)

		first_byte = raw_frame[0]

		current_byte_idx = 0
		index_current_byte_idx = 0
		name_current_byte_idx = 0
		value_current_byte_idx = 0
		next_field = None

		def calc_multi_byte_value(raw_frame, prefix_bit_length):
			prefix_value = 2 ** prefix_bit_length - 1
			current_byte_idx = 0
			value_bin = ""
			while True:
				current_byte = bin_padding(bin(raw_frame[current_byte_idx]).replace("0b", ""))
				value_bin = current_byte[1:] + value_bin
				current_byte_idx += 1
				if current_byte[0] == "0":
					break
			value = int(value_bin, 2) + prefix_value
			return (value, current_byte_idx)


		# Indexed Header Field
		if first_byte & 0x80 == 0x80:
			if first_byte & 0x7f == 0x7f :
				index, current_byte_idx = calc_multi_byte_value(raw_frame[1:], len(first_byte[1:]))
			else:
				index = first_byte ^ 0x80
			field = Field(0, index)

			if len(raw_frame[1:]) != 0:
				next_field = load_next_field(raw_frame[1+current_byte_idx:])

		# Literal Header Field and Maximum Dynamic Table Size Change
		else:
			# Literal Header Field with Incremental Indexing
			if first_byte & 0x40 == 0x40:
				if first_byte & 0x3f == 0x3f:
					index, index_current_byte_idx = calc_multi_byte_value(raw_frame[1:], len(first_byte[2:]))
				else:
					index = first_byte ^ 0x40

				# New Name
				if index == 0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1+index_current_byte_idx:])
					if name_h:
						name = decode(name, self.STATIC_HUFFMAN_REVERSE_TABLE)

					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+index_current_byte_idx+name_length+name_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(2, name=name, name_h=name_h, value=value, value_h=value_h)

					if len(raw_frame[3+name_length+value_length:]) != 0:
						next_field = load_next_field(raw_frame[3+index_current_byte_idx+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
					
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1+index_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(1, index=index, value=value, value_h=value_h)
					
					if len(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:]) != 0:
						next_field = load_next_field(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:])


			# Literal Header Field without Indexing
			elif first_byte < 0x10:
				if first_byte == 0xf:
					index, index_current_byte_idx = calc_multi_byte_value(raw_frame[1:], 4)
				else:
					index = first_byte

				# New Name
				if index == 0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1+index_current_byte_idx:])
					if name_h:
						name = decode(name, self.STATIC_HUFFMAN_REVERSE_TABLE)
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+index_current_byte_idx+name_length+name_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(4, value=value, value_h=value_h, name=name, name_h=name_h)

					if len(raw_frame[3+index_current_byte_idx+name_length+value_length+name_current_byte_idx+value_current_byte_idx:]) != 0:
						next_field = load_next_field(raw_frame[3+index_current_byte_idx+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
				
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1+index_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(3, index=index, value=value, value_h=value_h)

					if len(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:]) != 0:
						next_field = load_next_field(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:])
			
			# Literal Header Field Never Indexed
			elif first_byte & 0x10 == 0x10:
				if first_byte == 0xf:
					index, index_current_byte_idx = calc_multi_byte_value(raw_frame[1:], 4)
				else:
					index = first_byte

				# New Name
				if index==0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1+index_current_byte_idx:])
					if name_h:
						name = decode(name, self.STATIC_HUFFMAN_REVERSE_TABLE)
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+index_current_byte_idx+name_length+name_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(6, name=name, name_h=name_h, value=value, value_h=value_h)

					if len(raw_frame[3+index_current_byte_idx+name_length+value_length+name_current_byte_idx+value_current_byte_idx:]) != 0:
						next_field = load_next_field(raw_frame[3+index_current_byte_idx+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
				
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1+index_current_byte_idx:])
					if value_h:
						value = decode(value, self.STATIC_HUFFMAN_REVERSE_TABLE)
					field = Field(5, index=index, value=value, value_h=value_h)

					if len(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:]) != 0:
						next_field = load_next_field(raw_frame[2+index_current_byte_idx+value_length+value_current_byte_idx:])

			# Maximum Dynamic Table Size Change
			elif first_byte & 0x20 == 0x20:
				if first_byte ^ 0x20 == 0x1f:
					max_size, current_byte_idx = calc_multi_byte_value(raw_frame[1:], 5)
				else:
					max_size = first_byte ^ 0x20
				field = Field(7, max_size=max_size)

				if len(raw_frame[1+current_byte_idx:]) != 0:
					next_field = load_next_field(raw_frame[1+current_byte_idx:])

		fields = [field]
		if next_field:
			fields += next_field
		return fields


	def get_raw_frame(self):
		if self.field_type == 0:
			if self.index >= 2**7 - 1:
				print("Multi bytes length is not supported now")
			field_byte_str = "1" + bin_padding(bin(self.index).replace("0b", ""), 7)
			return int(field_byte_str, 2).to_bytes(1, "big")
		elif self.field_type == 1:
			first_bit_str = "01" + bin_padding(bin(self.index).replace("0b", ""), 6)
			first_bytes = int(first_bit_str, 2).to_bytes(1, "big")

			if self.value_h:
				value_h = "1"
			else:
				value_h = "0"
			
			value = bytes(self.value, "ascii")

			length = len(value)
			if length >= 2**7 - 1:
				print("Multi bytes length is not supported now")
				raise Exception
			length_bit_str = bin_padding(bin(length).replace("0b", ""), 7)
			value_length_bit_str = value_h + length_bit_str
			value_length_bytes = int(value_length_bit_str, 2).to_bytes(1, "big")
			
			return first_bytes + value_length_bytes + value

		elif self.field_type == 2:
			first_bit_str = "01000000"
			first_bytes = int(first_bit_str, 2).to_bytes(1, "big")

			if self.name_h:
				name_h = "1"
			else:
				name_h = "0"

			name = bytes(self.name, "ascii")
			name_length = len(name)
			if name_length >= 2**7 - 1:
				print("Multi bytes length is not supported now")
				raise Exception
			name_length_bit_str = name_h + bin_padding(bin(name_length).replace("0b", ""), 7)
			name_length_bytes = int(name_length_bit_str, 2).to_bytes(1, "big")

			if self.value_h:
				value_h = "1"
			else:
				value_h = "0"

			value = bytes(self.value, "ascii")
			value_length = len(value)
			if value_length >= 2**7 - 1:
				print("Multi bytes length is not supported now")
				raise Exception
			value_length_bit_str = value_h + bin_padding(bin(value_length).replace("0b", ""), 7)
			value_length_bytes = int(value_length_bit_str, 2).to_bytes(1, "big")
			
			return first_bytes + name_length_bytes + name + value_length_bytes + value

		else:
			print("Type %s is not supported now"%(self.field_type_str))
			return b""
		

	def __str__(self):
		base = "----------\r\nType: %s(%d)\r\n" % (
			self.field_type_str,
			self.field_type
		)
		if "index" in self.__dict__:
			base += "Index: %d\r\n"%(self.index)

		if "name_h" in self.__dict__:
			base += "Name Huffman: %d\r\n"%(int(self.name_h))

		if "name" in self.__dict__:
			base += "Name: %s\r\n"%(self.name)
		
		if "value_h" in self.__dict__:
			base += "Value Huffman: %d\r\n"%(int(self.value_h))

		if "value" in self.__dict__:
			base += "Value: %s\r\n"%(self.value)

		if "max_size" in self.__dict__:
			base += "Max size: %d\r\n"%(self.max_size)
		return base


	def __repr__(self):
		if self.field_type == 0:
			return "<%s:%d>"%(self.field_type_str, self.index)
		elif self.field_type in  [1, 2, 3, 4, 5, 6]:
			if self.field_type in [1, 3, 5]:
				return "<%s,index:%d,value:%s>"%(self.field_type_str, self.index, self.value)
			else:
				return "<%s,name:%s,value:%s>"%(self.field_type_str, self.name, self.value)
		else:
			return "<%s:%d>"%(self.field_type_str, self.max_size)


class Headers:
	exclusive_flag = 0x80000000

	def __init__(self, fields, is_exclusive=None, stream_dependency=None, weight=None, priority=None, padding_length=0, is_end_stream=False, is_end_headers=True):
		self.fields = fields
		if is_exclusive or stream_dependency:
			if not is_exclusive and not stream_dependency:
				print("Please specify both is_exclusive and stream_dependency")
				raise Exception
			else:
				self.is_exclusive = is_exclusive
				self.stream_dependency = stream_dependency
		self.weight = weight
		self.priority = priority
		self.padding_length = padding_length
		self.is_end_stream = is_end_stream
		self.is_end_headers = is_end_headers

	
	@classmethod
	def load_raw_frame(cls, raw_frame, flags=None):
		
		if flags:
			if is_flagged(flags, 0b1):
				is_end_stream = True
			else:
				is_end_stream = False

			#END_HEADERS
			if is_flagged(flags, 0b100):
				is_end_headers = True
			else:
				is_end_headers = False

			#padded
			if is_flagged(flags, 0b1000):
				padding_length = raw_frame[0]
				raw_frame = raw_frame[1:-padding_length]
			else:
				padding_length = 0

			is_exclusive = None
			stream_dependency = None
			#priority
			if is_flagged(flags, 0b10000):
				exclusive_and_stream_dependency = int.from_bytes(raw_frame[0:4], "big")
				if exclusive_and_stream_dependency & cls.exclusive_flag == cls.exclusive_flag:
					is_exclusive = True
					stream_dependency = exclusive_and_stream_dependency ^ cls.exclusive_flag
				else:
					is_exclusive = False
					stream_dependency = exclusive_and_stream_dependency
		
		fields = Field.load_raw_frame(raw_frame)
		return Headers(
			fields=fields,
			is_exclusive=is_exclusive,
			stream_dependency=stream_dependency,
			padding_length=padding_length,
			is_end_headers=is_end_headers,
			is_end_stream=is_end_stream
			)


	@classmethod
	def load_table(cls, static_fields, dynamic_fileds, is_end_headers, is_end_stream):
		fields = []

		for field_index in static_fields:
			fields.append(Field(0, index=int(field_index)))
		
		for field_dict in dynamic_fileds.values():
			if "original_index" in field_dict:
				fields.append(Field(1, index=int(field_dict["original_index"]), value=field_dict["value"], value_h=False))
			else:
				fields.append(Field(2, name=field_dict["name"], name_h=False, value=field_dict["value"], value_h=False))

		return Headers(
			fields=fields,
			is_end_headers=is_end_headers,
			is_end_stream=is_end_stream
			)


	def get_raw_frame(self):
		raw_frame = b""

		for field in self.fields:
			raw_frame += field.get_raw_frame()
		return raw_frame


	def __repr__(self):
		return "<Headers object that has " + str(len(self.fields)) + " fields>"