import struct

from .data import Data
from .settings import Settings
from .headers import Headers

from ..utils.bin import is_bin, bin_padding
from ..utils.flags import set_flag


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
		self.frame_type = frame_type
		self.frame_type_str = self.FRAME_TYPES[str(self.frame_type)]
		if type(flags) == int:
			self.flags = bin_padding(bin(flags).replace("0b", ""))
		elif type(flags) == str and is_bin(flags):
			self.flags = flags
		self.stream_identifier = stream_identifier
		self.payload = payload


	@classmethod
	def load_raw_frame(cls, raw_frame):
		def load_payload(frame_type, payload):
			if frame_type == 0:
				payload = cls.__load__data_frame(cls, payload, flags)
			elif frame_type == 1:
				payload = cls.__load_headers_frame(cls, payload, flags)
			elif frame_type == 4:
				payload = cls.__load_settings_frame(cls, payload)
			elif frame_type == 8:
				payload = int.from_bytes(payload, byteorder="big")
				payload = b""

			return payload

		length = int.from_bytes(raw_frame[0:3], byteorder="big")
		frame_type = raw_frame[3]
		flags = raw_frame[4]
		flags = bin_padding(bin(flags).replace("0b", ""))
		stream_identifier = int.from_bytes(raw_frame[5:9], byteorder="big")
		payload = raw_frame[9:]

		
		if len(payload) == length:
			payload = load_payload(frame_type, payload)
			frame = Frame(frame_type, flags, stream_identifier, payload)
			return [frame]
		else:
			payload, next_raw_frame = payload[:length], payload[length:]
			payload = load_payload(frame_type, payload)

			frame = Frame(frame_type, flags, stream_identifier, payload)
			next_frame = Frame.load_raw_frame(next_raw_frame)
			frames = [frame]
			if next_frame:
				frames += next_frame
			return frames

	def get_raw_frame(self):
		raw_frame = struct.pack(
			"!2Bi",
			self.frame_type,
			int(self.flags, 2),
			self.stream_identifier
		)

		if self.frame_type == 1:
			raw_frame = self.payload.get_raw_frame()
		elif self.frame_type == 4:
			raw_frame += b"".join(frame.get_raw_frame() for frame in self.payload)
		else:
			if type(self.payload) == bytes:
				raw_frame += self.payload
			else:
				raw_frame += bytes(self.payload, "utf-8")

		length = len(raw_frame)
		length_bytes = struct.pack(
			"!BH",
			*divmod(length, 1<<16)
		)

		return length_bytes + raw_frame


	def __str__(self):
		return "----------\r\nframe_type: %s(%d)\r\nlength: %d\r\nflags: 0b%s\r\nstream_identifier: %d\r\npayload: %s"%(
			self.frame_type_str,
			self.frame_type,
			self.length,
			self.flags,
			self.stream_identifier,
			self.payload
			)

	
	def __load__data_frame(self, payload, flags):
		data = Data.load_raw_frame(payload, flags)
		return data


	def __load_settings_frame(self, payload):
		frame_list = []

		for i in range(0, len(payload), 6):
			frame_list.append(Settings(payload[i:i+6]))

		return frame_list


	def __load_headers_frame(self, payload, flags):
		headers = Headers.load_raw_frame(payload, flags)
		return headers


	@classmethod
	def create_frame(cls, payload, stream_identifier):
		flags = "00000000"

		if isinstance(payload, Headers):
			frame_type = 1

			if payload.is_end_stream:
				flags = set_flag(flags, 0)
			
			if payload.is_end_headers:
				flags = set_flag(flags, 2)

		return Frame(frame_type, flags, stream_identifier, payload)