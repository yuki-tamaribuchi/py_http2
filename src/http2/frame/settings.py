from ..utils.flags import is_flagged

class SettingField:
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
		self.value = value

	def __str__(self):
		return "%s(%d): %s"%(
			self.IDENTIFIERS[str(self.identifier)],
			self.identifier,
			str(self.value)
		)



class Settings:
	def __init__(self, fields, is_ack=False):
		if fields and is_ack:
			print("Do not set fields in acknowledge setting frame")
		self.fields = fields
		self.is_ack = is_ack
	

	@classmethod
	def load_raw_frame(self, raw_frame, flags):
		if is_flagged(flags, 0b1):
			is_ack = True
		else:
			is_ack = False

		fields = []
		for i in range(0, len(raw_frame), 6):
			identifier = int.from_bytes(raw_frame[i:i+2], "big")
			value = int.from_bytes(raw_frame[i+2:i+6], "big")
			setting_field = SettingField(identifier, value)
			fields.append(setting_field)
			
		return Settings(fields, is_ack)

	def get_raw_frame(self):
		import struct
		raw_frame = b""

		if self.fields:
			for field in self.fields:
				raw_frame += struct.pack(
					"!HI",
					field.identifier,
					field.value
				)

		return raw_frame
	

	def __repr__(self):
		return "Settings frame has %s fields"%(
			len(self.fields)
		)