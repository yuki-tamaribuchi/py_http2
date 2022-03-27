import struct

from ..utils.flags import is_flagged

class Field:
	FIELD_TYPES = {
		"0": "INDEX HEADER FIELD"
	}
	def __init__(self, field_type:int, index=None):
		self.field_type = field_type
		if self.field_type == 0:
			self.field_type_str = self.FIELD_TYPES[str(self.field_type)]
			if index is None:
				print("Please specify index")
				raise Exception
			self.index = index

	
	def get_raw_frame(self):
		if field_type == 0:
			field_byte_str = "0" + bin(self.index).replace("0b", "")
			return bytes(int(field_byte_str), 2)
		else:
			print("Type %s is not supported now"%(self.field_type_str))
			raise Exception
		

	def __str__(self):
		base = "----------\r\nType: %s(%d)\r\n" % (
			self.field_type_str,
			self.field_type
		)
		
		if self.field_type == 0:
			return base + "Index: %d" % (
				self.index
			)


class Headers:
	def __init__(self, stream_dependency, weight, priority, padding_length=0, is_end_stream=False, is_end_headers=False):
		self.stream_dependency = stream_dependency
		self.weight = weight
		self.priority = priority
		self.padding_length = padding_length
		self.is_end_stream = is_end_stream
		self.is_end_headers = is_end_headers

	
	@classmethod
	def load_raw_frame(cls, raw_frame, flags=None):
		if flags:
			#padded
			if is_flagged(flags, 4):
				print("Padded frame process is not implemented now")
				raise Exception
			#priority
			if is_flagged(flags, 6):
				print("Frame with priority is not supported now")
				raise Exception



		first_byte = bin(raw_frame[0])

		if first_byte[2] == "1":
			index = int(first_byte[3:], 2)
			field = Field(0, index)

			if len(raw_frame[1:]) > 0:
				next_raw_frame = raw_frame[1:]
				next_field = Headers.load_raw_frame(next_raw_frame)
		else:
			pass


		fields = [field]
		if next_field:
			for f in next_field:
				fields.append(f)
		return fields