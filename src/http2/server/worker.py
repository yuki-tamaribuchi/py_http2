from threading import Thread

from ..request import Request
from ..response import Response
from ..frame import Frame


def recv_request(client_sock):
	raw_request = client_sock.recv(4096)
	return raw_request


def send_response(client_sock, response):
	client_sock.send(response)
	return True


def switch_protocol(client_sock, request):
	if not "Upgrade" in request.options and not request.options["Upgrade"] == "h2c":
		print("h2c error")
		raise Exception

	if not "HTTP2-Settings" in request.options:
		print("Request has no HTTP2-Settings filed")
		raise Exception

	upgrade_options_dict = {
		"Connection": "Upgrade",
		"Upgrade": "h2c"
	}
	response = Response("HTTP/1.1", 101, upgrade_options_dict)

	if not send_response(client_sock, response.get_raw_response()):
		print("Respone send error")
		raise Exception

	return True


class Worker(Thread):
	def __init__(self, client_sock):
		self.client_sock = client_sock
	
	def start(self):
		raw_request = recv_request(self.client_sock)
		if b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n" in raw_request:
			print("HTTP/2.0 prior knowledge is not supported now")
			raise Exception
		
		request = Request(raw_request)


		#Switch Protocol if request http version 1.1
		if request.version == "HTTP/1.1":
			if "Upgrade" in request.options:
				if not switch_protocol(self.client_sock, request):
					print("Switching protocol error")
					raise Exception
			else:
				send_response(self.client_sock, b"HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n")
				return
				
		

		#Recieve preface
		raw_request = recv_request(self.client_sock)
		if not raw_request == b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n':
			print("Preface error")
			raise Exception

		#Recieve SETTINGS frame
		raw_request = recv_request(self.client_sock)
		frame = Frame.load_raw_frame(raw_request)


		#Send preface SETTINGS frame
		frame = Frame(0x4, 0x0, 0x0, b"")
		if not send_response(self.client_sock, frame.get_raw_frame()):
			print("Preface send error")
			raise Exception


		#Recieve WINDOW_UPDATE frame
		raw_request = recv_request(self.client_sock)
		frame = Frame.load_raw_frame(raw_request)
		assert(frame.frame_type == 8)
		windows_size = int.from_bytes(frame.payload, "big")
		print("Window size: ", windows_size)

		#Recieve empty SETTINGS frame
		raw_request = recv_request(self.client_sock)
		frame = Frame.load_raw_frame(raw_request)