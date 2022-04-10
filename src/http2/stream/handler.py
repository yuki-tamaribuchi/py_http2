from threading import Thread


from ..frame import Frame
from ..stream.stream import Stream
from ..utils.flags import is_flagged


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
		"half_closed_local": 4,
		"closed": 5
	}
	
	def __init__(self, client_sock, request_queue):
		self.client_sock = client_sock
		self.request_queue = request_queue
		self.request_stream_list = []
		self.response_stream_list = []
		self.max_current_streams = None
		self.current_max_stream_identification = None
		self.window_size = None
		self.max_window_size = None
		self.header_table_size = None
		self.is_push_enabled = None
		self.max_header_list_size = None


	def add_preface_frame(self, frames):
		for frame in frames:
			self.__handle_request_frame(frame)
		

	def run(self):
		handle_request_thread = Thread(target=self.__handle_request)
		handle_response_thread = Thread(target=self.__handle_response)

		handle_request_thread.start()
		handle_response_thread.start()
		

	def __handle_request(self):
		while True:
			raw_frame = recv_request(self.client_sock)
			if raw_frame == b"":
				break
			frames = Frame.load_raw_frame(raw_frame)
			for frame in frames:
				if not self.__handle_request_frame(frame):
					print("Handle error")
					raise Exception


	def __handle_request_frame(self, frame):
		# DATA frame
		if frame.frame_type == 0:
			pass

		# HEADERS frame
		elif frame.frame_type == 1:
			if is_flagged(frame.flags, 0):
				state = self.STREAM_STATES["half_closed_remote"]
			else:
				state = self.STREAM_STATES["open"]
			stream = Stream(state, frame.stream_identifier)

			stream.add_request_headers_to_table(frame.payload)





			request = stream.request_headers_table.create_request_instance()
			self.request_queue.put((request, stream.stream_identifier))





			self.__add_request_stream_to_list(stream)

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


	def __handle_response(self):
		while True:
			pass

	
	def __handle_response_frame(self):
		pass


	def __get_request_stream_by_id(self, id):
		for stream in self.request_stream_list:
			if stream.stream_identifier == id:
				return stream
		return None

	def __add_request_stream_to_list(self, stream):
		self.request_stream_list.append(stream)

	
	def __add_response_stream_to_list(self, stream):
		self.response_stream_list.append(stream)

	
	def __recieve_frame(self, frame):
		pass

	
	def __send_frame(self):
		pass