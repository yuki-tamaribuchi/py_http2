class Request:
	def __init__(self, raw_request):
		if b"HTTP/1.0" in raw_request or b"HTTP/1.1" in raw_request:
			raw_request = raw_request.decode("ascii")
			request_header, self.request_body = raw_request.split("\r\n\r\n")

			splitted_request_header = request_header.split("\r\n")

			request_line = splitted_request_header[0]
			request_options = splitted_request_header[1:]

			self.method, uri, self.version = request_line.split(" ")
			if len(uri)>1:
				self.uri = uri[1:]
			else:
				self.uri = ""

			self.options = {}
			for option in request_options:
				k, v = option.split(": ")
				self.options[k] = v
		
		elif b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n" in raw_request:
			self.version = "HTTP/2.0"
			self.is_preface = True
			self.raw_frame = raw_request.replace(b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n", b"")

		else:
			print("This request is not supported")
			print(raw_request)
			raise Exception
