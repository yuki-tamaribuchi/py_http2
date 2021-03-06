from threading import Thread


from ..request import Request

from ..frame import Frame
from ..stream.stream import Stream
from ..utils.flags import is_flagged
from ..frame.settings import Settings


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
	
	def __init__(self, client_sock, request_queue, response_queue):
		self.client_sock = client_sock
		self.request_queue = request_queue
		self.response_queue = response_queue
		self.stream_list = []
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

		handle_request_thread.join()
		handle_response_thread.join()


	def __handle_request(self):
		while True:
			raw_frame = recv_request(self.client_sock)
			if not raw_frame == b"":
				frames = Frame.load_raw_frame(raw_frame)
				for frame in frames:
					if not self.__handle_request_frame(frame):
						print("Handle error")
						raise Exception


	def __handle_request_frame(self, frame):
		# DATA frame
		if frame.frame_type == 0:
			stream_idx = self.__get_client_stream_index_by_id(frame.stream_identifier)
			self.stream_list[stream_idx].request_data = frame.payload.data

			if frame.payload.is_end_stream:
				stream = self.stream_list[stream_idx]
				request = self.__create_request_instance(stream)
				self.request_queue.put((request, stream.stream_identifier))

		# HEADERS frame
		elif frame.frame_type == 1:
			if is_flagged(frame.flags, 0):
				state = self.STREAM_STATES["half_closed_remote"]
			else:
				state = self.STREAM_STATES["open"]
			stream = Stream(state, frame.stream_identifier)

			stream.add_request_headers_to_table(frame.payload)

			if frame.payload.is_end_stream:
				request = self.__create_request_instance(stream)
				self.request_queue.put((request, stream.stream_identifier))

			self.__add_client_stream_to_list(stream)

		# SETTINGS frame
		elif frame.frame_type == 4:
			for field in frame.payload.fields:
				if field.identifier == 1:
					self.header_table_size = field.value
				elif field.identifier == 2:
					self.is_push_enabled = bool(field.value)
				elif field.identifier == 3:
					self.max_current_streams = field.value
				elif field.identifier == 4:
					self.windows_size = field.value
				elif field.identifier == 5:
					self.max_window_size = field.value
				elif field.identifier == 6:
					self.max_header_list_size = field.value
			settings_ack = Settings(fields=None, is_ack=True)
			settings_frame = Frame.create_frame(settings_ack, 0)
			#send_response(self.client_sock, settings_frame.get_raw_frame())
		
		# GOAWAY frame
		elif frame.frame_type == 7:
			print(frame)
			return True

		# WINDOW_UPDATE frame
		elif frame.frame_type == 8:
			self.window_size = frame.payload

		return True


	def __handle_response(self):
		while True:
			if not self.response_queue.empty():
				response, stream_identifier = self.response_queue.get()
				if not self.__handle_response_frame(response, stream_identifier):
					print("Response handler error")
					raise Exception

	
	def __handle_response_frame(self, response, stream_identifier):
		frames = []
		response_status = response.status
		response_options = response.options
		response_body = response.body


		stream_idx = self.__get_client_stream_index_by_id(stream_identifier)

		is_end_headers = True

		if response_body:
			is_end_stream = False
			self.stream_list[stream_idx].response_data = response_body
		else:
			is_end_stream = True

		self.stream_list[stream_idx].response_headers_table.load_response(response_status, response_options)
		headers = self.stream_list[stream_idx].response_headers_table.create_headers(is_end_headers=is_end_headers, is_end_stream=is_end_stream)
		headers_frame = Frame.create_frame(headers, stream_identifier)
		frames.append(headers_frame)

		if response_body:
			data = self.stream_list[stream_idx].create_response_data_frame(padding_length=None, is_end_stream=True)
			data_frame = Frame.create_frame(data, stream_identifier)
			frames.append(data_frame)

		raw_response = b""
		for frame in frames:
			raw_response += frame.get_raw_frame()

		if not send_response(self.client_sock, raw_response):
			print("send_response error")
			raise Exception
		
		self.stream_list[stream_idx].state = self.STREAM_STATES["closed"]
		return True



	def __get_client_stream_index_by_id(self, id):
		for i, stream in enumerate(self.stream_list):
			if stream.stream_identifier == id:
				return i
		return None

	def __add_client_stream_to_list(self, stream):
		self.stream_list.append(stream)

	
	def __add_server_stream_to_list(self, stream):
		self.server_stream_list.append(stream)

	
	def __recieve_frame(self, frame):
		pass

	
	def __send_frame(self):
		pass

	
	def __create_request_instance(self, stream):
		headers_dict = stream.request_headers_table.create_headers_dict()

		if ":authority" in headers_dict:
			authority = headers_dict.pop(":authority")
		
		if ":scheme" in headers_dict:
			scheme = headers_dict.pop(":scheme")
		
		if ":method" in headers_dict:
			method = headers_dict.pop(":method")

		if ":path" in headers_dict:
			uri = headers_dict.pop(":path")

		options = headers_dict

		if stream.request_data:
			body = stream.request_data
		else:
			body = None


		return Request(
			version="HTTP/2.0",
			authority=authority,
			scheme=scheme,
			method=method,
			uri=uri,
			options=options,
			body=body
		)