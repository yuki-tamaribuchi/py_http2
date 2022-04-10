def is_flagged(flags, bit_n):
	assert(bit_n >= 0 and bit_n <=7)
	return bool(int(flags[7-bit_n]))