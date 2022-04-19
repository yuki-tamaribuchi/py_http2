class Settings:
	IDENTIFIERS = {
		"1": "SETTINGS_HEADER_TABLE_SIZE",
		"2": "SETTINGS_ENABLE_PUSH",
		"3": "SETTINGS_MAX_CONCURRENT_STREAMS", 
		"4": "SETTINGS_INITIAL_WINDOW_SIZE",
		"5": "SETTINGS_MAX_WINDOW_SIZE",
		"6": "SETTINGS_MAX_HEADER_LIST_SIZE"
	}

	def __init__(self, identifier, value):
		self.identifier = identifier
		self.identifier_str = self.IDENTIFIERS[str(self.identifier)]
		self.value = value
	

	@classmethod
	def load_raw_frame(self, raw_frame):
		frame_list = []

		for i in range(0, len(raw_frame), 6):
			identifier = int.from_bytes(raw_frame[0:2], "big")
			value = int.from_bytes(raw_frame[2:], "big")
			frame = Settings(identifier, value)
			frame_list.append(frame)
		return frame_list

	def get_raw_frame(self):
		import struct
		raw_frame = struct.pack(
			"!HI",
			self.identifier,
			self.value
		)
		return raw_frame
	

	def __repr__(self):
		return "%s(%d): %d"%(
			self.identifier_str,
			self.identifier,
			self.value
		)