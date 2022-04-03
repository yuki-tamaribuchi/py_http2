def is_flagged(flags, bit_n):
	assert(bit_n >= 0 and bit_n <=8)
	return bool(int(flags[8-bit_n]))