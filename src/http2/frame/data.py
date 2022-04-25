from ..utils.flags import is_flagged

class Data:
	def __init__(self, data, padding_length, is_end_stream=False):
		assert(type(data) == bytes)
		self.data = data
		self.padding_length = padding_length
		self.is_end_stream = is_end_stream

	
	@classmethod
	def load_raw_frame(self, raw_frame, flags):
		if is_flagged(flags, 0b1):
			is_end_stream = True
		else:
			is_end_stream = False

		if is_flagged(flags, 0b1000):
			padding_length = raw_frame[0]
			raw_frame = raw_frame[1:padding_length]
		else:
			padding_length = 0

		return Data(
			data=raw_frame,
			padding_length=padding_length,
			is_end_stream=is_end_stream
		)

	def get_raw_frame(self):
		if self.padding_length:
			print("Padding is not supported now")
			raise Exception

		return self.data