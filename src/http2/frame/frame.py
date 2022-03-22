import struct

from .settings import Settings

class Frame:
	FRAME_TYPES = {
			"0": "DATA",
			"1": "HEADERS",
			"2": "PRIORITY",
			"3": "RST_STREAM",
			"4": "SETTINGS",
			"5": "PUSH_PROMISE",
			"6": "PING",
			"7": "GOAWAY",
			"8": "WINDOW_UPDATE",
			"9": "CONTINUATION",
			"10": "ALTSVC",
			"12": "ORIGIN"
		}
	
	def __init__(self, frame_type, flags, stream_identifier, payload):
		self.length = len(payload)
		self.frame_type = frame_type
		self.frame_type_str = self.FRAME_TYPES[str(self.frame_type)]
		self.flags = flags
		self.stream_identifier = stream_identifier

		if self.frame_type == 4:
			self.payload = self.__load_settings_frame(payload)
		else:
			self.payload = payload


	@classmethod
	def load_raw_frame(cls, raw_frame):
		length = int.from_bytes(raw_frame[0:3], byteorder="big")
		frame_type = raw_frame[3]
		flags = raw_frame[4]
		stream_identifier = int.from_bytes(raw_frame[5:9], byteorder="big")
		payload = raw_frame[9:]
		assert(length==len(payload))

		return Frame(frame_type, flags, stream_identifier, payload)

	
	def get_raw_frame(self):
		raw_frame = struct.pack(
			"!BH2Bi",
			*divmod(self.length, 1<<16),
			self.frame_type,
			self.flags,
			self.stream_identifier
		)

		if self.frame_type == 4:
			raw_frame += b"".join(frame.get_raw_frame() for frame in self.payload)
		else:
			if type(self.payload) == bytes:
				raw_frame += self.payload
			else:
				raw_frame += bytes(self.payload, "utf-8")

		return raw_frame


	def __str__(self):
		return "length: %d\r\nframe_type: %s(%d)\r\nflags: %d\r\nstream_identifier: %d\r\npayload: %s"%(
			self.length,
			self.frame_type_str,
			self.frame_type,
			self.flags,
			self.stream_identifier,
			self.payload
			)


	def __load_settings_frame(self, payload):
		frame_list = []

		for i in range(0, len(payload), 6):
			frame_list.append(Settings(payload[i:i+6]))

		return frame_list
