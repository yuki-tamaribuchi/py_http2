def is_flagged(flags, flag_n):
	assert(flag_n >= 0b00000000 and flag_n <=0b11111111)
	if flags & flag_n == flag_n:
		return True
	return False