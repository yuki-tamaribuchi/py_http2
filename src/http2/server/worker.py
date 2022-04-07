from threading import Thread

from ..request import Request
from ..response import Response
from ..frame import Frame
from ..stream.handler import StreamHandler


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
		request = Request.load_raw_request(raw_request)


		#Switch Protocol if request http version 1.1
		if request.version == "HTTP/1.1":
			if "Upgrade" in request.options:
				if not switch_protocol(self.client_sock, request):
					print("Switching protocol error")
					raise Exception
				raw_request = recv_request(self.client_sock)
				request = Request.load_raw_request(raw_request)
			else:
				send_response(self.client_sock, b"HTTP/1.1 505 HTTP Version Not Supported\r\n\r\n")
				return


		if request.version == "HTTP/2.0" and request.is_preface:
			if request.raw_frame:
				preface_frame = Frame.load_raw_frame(request.raw_frame)
			else:
				preface_frame = None

			frame = Frame(0x4, 0x0, 0x0, b"")
			if not send_response(self.client_sock, frame.get_raw_frame()):
				print("Preface send error")
				raise Exception


			handler = StreamHandler(self.client_sock)
			if preface_frame:
				handler.add_preface_frame(preface_frame)
			handler.run()
			return