def is_bin(data):
	for d in data:
		if not d in [0, 1]:
			return False
	return True

def bin_padding(data, total_length=8):
	padding_length = total_length - len(data)
	return "".join(["0" for _ in range(padding_length)]) + data