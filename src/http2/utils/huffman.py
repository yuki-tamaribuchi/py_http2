from .bin import bin_padding

def decode(data, reverse_table):
	data_bin = "".join([bin_padding(bin(d).replace("0b", "")) for d in data])

	value = ""
	current_bin = ""
	for b in data_bin:
		current_bin += b
		if current_bin in reverse_table:
			value += reverse_table[current_bin]
			current_bin = ""
	value = bytes(value, "ascii")
	return value