from .bin import bin_padding


def encode(data, table):
	data = data.decode("ascii")
	encoded_data_bin = ""
	for d in data:
		encoded_data_bin += table[d]

	if len(encoded_data_bin) % 8 != 0:
		encoded_data_bin += "".join(["1" for _ in range(8-len(encoded_data_bin)%8)])

	encoded_data = b""
	for i in range(len(encoded_data_bin), 0, -8):
		one_byte_bin = encoded_data_bin[i-8:i]
		if len(one_byte_bin) != 0:
			one_byte_int = int(one_byte_bin, 2)
			encoded_data = one_byte_int.to_bytes(1, "little") + encoded_data
	
	last_byte = encoded_data_bin[:i]

	return encoded_data



def decode(data, reverse_table):
	data_bin = "".join([bin_padding(bin(d).replace("0b", "")) for d in data])

	value = ""
	current_bin = ""
	for b in data_bin:
		current_bin += b
		if len(current_bin)>=4:
			if current_bin in reverse_table:
				value += reverse_table[current_bin]
				current_bin = ""
	value = bytes(value, "ascii")
	return value