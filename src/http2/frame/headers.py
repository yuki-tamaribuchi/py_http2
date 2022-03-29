import struct

from ..utils.flags import is_flagged
from ..utils.bin import bin_padding

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
	STATIC_HEADER_FIELDS = {
		"1": {"name": ":authority", "value": ""},
		"2": {"name": ":method", "value": "GET"},
		"3": {"name": ":method", "value": "POST"},
		"4": {"name": ":path", "value": "/"},
		"5": {"name": ":path", "value": "/index.html"},
		"6": {"name": ":scheme", "value": "http"},
		"7": {"name": ":scheme", "value": "https"},
		"8": {"name": ":status", "value": "200"},
		"9": {"name": ":status", "value": "204"},
		"10": {"name": ":status", "value": "206"},
		"11": {"name": ":status", "value": "304"},
		"12": {"name": ":status", "value": "400"},
		"13": {"name": ":status", "value": "404"},
		"14": {"name": ":status", "value": "500"},
		"15": {"name": "accept-charset", "value": ""},
		"16": {"name": "accept-encoding", "value": "gzip, deflate"},
		"17": {"name": "accept-language", "value": ""},
		"18": {"name": "accept-ranges", "value": ""},
		"19": {"name": "accept", "value": ""},
		"20": {"name": "access-control-allow-origin", "value": ""},
		"21": {"name": "age", "value": ""},
		"22": {"name": "allow", "value": ""},
		"23": {"name": "authorization", "value": ""},
		"24": {"name": "cache-control", "value": ""},
		"25": {"name": "content-disposition", "value": ""},
		"26": {"name": "content-encoding", "value": ""},
		"27": {"name": "content-language", "value": ""},
		"28": {"name": "content-length", "value": ""},
		"29": {"name": "content-location", "value": ""},
		"30": {"name": "content-range", "value": ""},
		"31": {"name": "content-type", "value": ""},
		"32": {"name": "cookie", "value": ""},
		"33": {"name": "date", "value": ""},
		"34": {"name": "etag", "value": ""},
		"35": {"name": "expect", "value": ""},
		"36": {"name": "expires", "value": ""},
		"37": {"name": "from", "value": ""},
		"38": {"name": "host", "value": ""},
		"39": {"name": "if-match", "value": ""},
		"40": {"name": "if-modified-since", "value": ""},
		"41": {"name": "if-none-match", "value": ""},
		"42": {"name": "if-range", "value": ""},
		"43": {"name": "if-unmodified-since", "value": ""},
		"44": {"name": "last-modified", "value": ""},
		"45": {"name": "link", "value": ""},
		"46": {"name": "location", "value": ""},
		"47": {"name": "max-forwards", "value": ""},
		"48": {"name": "proxy-authenticate", "value": ""},
		"49": {"name": "proxy-authorization", "value": ""},
		"50": {"name": "range", "value": ""},
		"51": {"name": "referer", "value": ""},
		"52": {"name": "refresh", "value": ""},
		"53": {"name": "retry-after", "value": ""},
		"54": {"name": "server", "value": ""},
		"55": {"name": "set-cookie", "value": ""},
		"56": {"name": "strict-transport-security", "value": ""},
		"57": {"name": "transfer-encoding", "value": ""},
		"58": {"name": "user-agent", "value": ""},
		"59": {"name": "vary", "value": ""},
		"60": {"name": "via", "value": ""},
		"61": {"name": "www-authenticate", "value": ""}
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
		
		if self.field_type in [1, 2, 3, 4, 5, 6]:
			if value is None:
				print("Please specify value")
				raise Exception
			if value_h is None:
				print("Please specify value_h")
				raise Exception
			self.value = value
		
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
				name_length, current_byte_idx = calc_multi_byte_value(raw_frame[1:])
			else:
				name_length = int(h_and_name_length_bin[1:], 2)
			name = raw_frame[1:1+name_length]
			return (name, name_h, name_length, current_byte_idx)

		def load_value(raw_frame):
			current_byte_idx = 0
			h_and_value_length_bin = bin_padding(bin(raw_frame[0]).replace("0b", ""))
			value_h = bool(int(h_and_value_length_bin[0]))
			if is_all_flagged(h_and_value_length_bin[1:]):
				value_length, current_byte_idx = calc_multi_byte_value(raw_frame[1:])
			else:
				value_length = int(h_and_value_length_bin[1:], 2)
			value = raw_frame[1:1+value_length]
			return (value, value_h, value_length, current_byte_idx)

		first_byte = bin(raw_frame[0]).replace("0b", "")
		first_byte = bin_padding(first_byte)

		current_byte_idx = 0
		name_current_byte_idx = 0
		value_current_byte_idx = 0
		next_field = None

		def calc_multi_byte_value(raw_frame):
			current_byte_idx = 0
			value_bin = ""
			while True:
				current_byte = bin_padding(bin(raw_frame[current_byte_idx]).replace("0b", ""))
				value_bin = current_byte[1:] + value_bin
				current_byte_idx += 1
				if current_byte[0] == "0":
					break
			value = int(value_bin, 2)
			return (value, current_byte_idx)

		# Indexed Header Field
		if first_byte[0] == "1":
			if first_byte[1:] == "1111111":
				index, current_byte_idx = calc_multi_byte_value(raw_frame[1:])
			else:
				index = int(first_byte[1:], 2)
			field = Field(0, index)

			if len(raw_frame[1:]) != 0:
				next_field = load_next_field(raw_frame[1+current_byte_idx:])

		# Literal Header Field and Maximum Dynamic Table Size Change
		else:
			# Literal Header Field with Incremental Indexing
			if first_byte[1] == "1":
				index = int(first_byte[2:8], 2)

				# New Name
				if index == 0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1:])
					if name_h:
						print("Huffman decoder is not implemented now")

					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+name_length+name_current_byte_idx:])
					if value_h:
						print("Huffman decoder is not implemented now")
					field = Field(2, name=name, name_h=name_h, value=value, value_h=value_h)

					if len(raw_frame[3+name_length+value_length:]) != 0:
						next_field = load_next_field(raw_frame[3+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
					
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1:])
					if value_h:
						print("Huffman decoder is not implemented now")
					field = Field(1, index=index, value=value, value_h=value_h)
					
					if len(raw_frame[2+value_length:]) != 0:
						next_field = load_next_field(raw_frame[2+value_length+value_current_byte_idx:])


			# Literal Header Field without Indexing
			elif first_byte[0:4] == "0000":
				index = int(first_byte[4:], 2)

				# New Name
				if index == 0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1:])
					if name_h:
						print("Huffman decoder is not implemeted now")
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+name_length+name_current_byte_idx:])
					if value_h:
						print("Huffman decoder is not implemeted now")
					field = Field(4, value=value, value_h=value_h, name=name, name_h=name_h)

					if len(raw_frame[3+name_length+value_length:]) != 0:
						next_field = load_next_field(raw_frame[3+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
				
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1:])
					if value_h:
						print("Huffman decoder is not implemented now")
					field = Field(3, index=index, value=value, value_h=value_h)

					if len(raw_frame[2+value_length:]) != 0:
						next_field = load_next_field(raw_frame[2+value_length+value_current_byte_idx:])
			
			# Literal Header Field Never Indexed
			elif first_byte[0:4] == "0001":
				index = int(first_byte[4:], 2)

				# New Name
				if index==0:
					name, name_h, name_length, name_current_byte_idx = load_name(raw_frame[1:])
					if name_h:
						print("Huffman decoder is not implemeted now")
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[2+name_length+name_current_byte_idx:])
					if value_h:
						print("Huffman decoder is not implemeted now")
					field = Field(6, name=name, name_h=name_h, value=value, value_h=value_h)

					if len(raw_frame[3+name_length+value_length:]) != 0:
						next_field = load_next_field(raw_frame[3+name_length+value_length+name_current_byte_idx+value_current_byte_idx:])
				
				# Indexed Name
				else:
					value, value_h, value_length, value_current_byte_idx = load_value(raw_frame[1:])
					if value_h:
						print("Huffman decoder is not implemeted now")
					field = Field(5, index=index, value=value, value_h=value_h)

					if len(raw_frame[2+value_length:]) != 0:
						next_field = load_next_field(raw_frame[2+value_length+value_current_byte_idx:])

			# Maximum Dynamic Table Size Change
			elif first_byte[0:3] == "001":
				if is_all_flagged(first_byte[3:]):
					max_size, current_byte_idx = calc_multi_byte_value(raw_frame[1:])
				else:
					max_size = int(first_byte[3:] ,2)
				field = Field(7, max_size=max_size)

				if len(raw_frame[1:]) != 0:
					next_field = load_next_field(raw_frame[1+current_byte_idx:])

		fields = [field]
		if next_field:
			fields += next_field
		return fields


	def get_raw_frame(self):
		if self.field_type == 0:
			field_byte_str = "0" + bin_padding(bin(self.index).replace("0b", ""), 7)
			return bytes(int(field_byte_str, 2))
		else:
			print("Type %s is not supported now"%(self.field_type_str))
			raise Exception
		

	def __str__(self):
		base = "----------\r\nType: %s(%d)\r\n" % (
			self.field_type_str,
			self.field_type
		)
		
		if self.field_type == 0:
			return base + "Index: %d" % (
				self.index
			)
		else:
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
	def __init__(self, fields, stream_dependency=None, weight=None, priority=None, padding_length=0, is_end_stream=False, is_end_headers=False):
		self.fields = fields
		self.stream_dependency = stream_dependency
		self.weight = weight
		self.priority = priority
		self.padding_length = padding_length
		self.is_end_stream = is_end_stream
		self.is_end_headers = is_end_headers

	
	@classmethod
	def load_raw_frame(cls, raw_frame, flags=None):
		
		if flags:
			#padded
			if is_flagged(flags, 4):
				print("Padded frame process is not implemented now")
				raise Exception
			#priority
			if is_flagged(flags, 6):
				print("Frame with priority is not supported now")
				raise Exception
		
		fields = Field.load_raw_frame(raw_frame)
		return Headers(fields)


	def __repr__(self):
		return "<Headers object that has " + str(len(self.fields)) + " fields>"