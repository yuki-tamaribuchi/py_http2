class Settings:
	IDENTIFIERS = {
		"1": "SETTINGS_HEADER_TABLE_SIZE",
		"2": "SETTINGS_ENABLE_PUSH",
		"3": "SETTINGS_MAX_CONCURRENT_STREAMS", 
		"4": "SETTINGS_INITIAL_WINDOW_SIZE",
		"5": "SETTINGS_INITIAL_WINDOW_SIZE",
		"6": "SETTINGS_MAX_HEADER_LIST_SIZE"
	}

	def __init__(self, payload):
		self.identifier = int.from_bytes(payload[0:2], "big")
		self.identifier_str = self.IDENTIFIERS[str(self.identifier)]
		self.value = int.from_bytes(payload[2:], "big")
	

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