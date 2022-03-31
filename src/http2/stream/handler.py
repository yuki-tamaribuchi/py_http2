from ..frame import Frame
from ..stream.stream import Stream


def recv_request(client_sock):
	raw_request = client_sock.recv(4096)
	return raw_request


def send_response(client_sock, response):
	client_sock.send(response)
	return True



class StreamHandler:
	STREAM_STATES = {
		"open": 0,
		"reserved_local": 1,
		"reserved_remote": 2,
		"half_closed_remote": 3,
		"half_clised_local": 4
	}
	
	def __init__(self, client_sock):
		self.client_sock = client_sock
		self.stream_instance_list = []
		self.max_current_streams = None
		self.current_max_stream_identification = 1
		self.window_size = None
		self.max_window_size = None
		self.header_table_size = None
		self.is_push_enabled = None
		self.max_header_list_size = None


	def add_preface_frame(self, frames):
		for frame in frames:
			self.__handle(frame)
		

	def run(self):
		while True:
			raw_frame = recv_request(self.client_sock)
			if raw_frame == b"":
				break
			frames = Frame.load_raw_frame(raw_frame)
			for frame in frames:
				if not self.__handle(frame):
					print("Handle error")
					raise Exception


	def __handle(self, frame):
		# DATA frame
		if frame.frame_type == 0:
			pass

		# HEADERS frame
		#elif frame.frame_type == 1:


		# SETTINGS frame
		elif frame.frame_type == 4:
			for s in frame.payload:
				if s.identifier == 0:
					pass
				elif s.identifier == 1:
					self.header_table_size = s.value
				elif s.identifier == 2:
					self.is_push_enabled = bool(s.value)
				elif s.identifier == 3:
					self.max_current_streams = s.value
				elif s.identifier == 4:
					self.windows_size = s.value
				elif s.identifier == 5:
					self.max_window_size = s.value
				elif s.identifier == 6:
					self.max_header_list_size = s.value

		# WINDOW_UPDATE frame
		elif frame.frame_type == 8:
			self.window_size = frame.payload

		return True



	def __add_stream(self, stream_instance):
		self.stream_instance_list.append(stream_instance)

	
	def __recieve_frame(self, frame):
		pass

	
	def __send_frame(self):
		pass