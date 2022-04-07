class Request:

	def __init__(self,
				version,
				method=None,
				uri=None,
				options=None,
				body=None,
				authority=None,
				scheme=None,
				is_preface=False,
				raw_frame=None
				):
		self.version = version
		self.method = method
		self.uri = uri
		self.options = options
		self.body = body
		self.authority = authority
		self.scheme = scheme
		self.is_preface = is_preface
		self.raw_frame = raw_frame

	@classmethod
	def load_raw_request(cls, raw_request):
		if b"HTTP/1.0" in raw_request or b"HTTP/1.1" in raw_request:
			raw_request = raw_request.decode("ascii")
			request_header, request_body = raw_request.split("\r\n\r\n")

			splitted_request_header = request_header.split("\r\n")

			request_line = splitted_request_header[0]
			request_options = splitted_request_header[1:]

			method, uri, version = request_line.split(" ")
			if len(uri)>1:
				uri = uri[1:]
			else:
				uri = ""

			options = {}
			for option in request_options:
				k, v = option.split(": ")
				options[k] = v

			return Request(
				version=version,
				method=method,
				uri=uri,
				options=options,
				body=request_body
			)
		
		elif b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n" in raw_request:
			version = "HTTP/2.0"
			is_preface = True
			raw_frame = raw_request.replace(b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n", b"")

			return Request(
				version=version,
				is_preface=is_preface,
				raw_frame=raw_frame
			)

		else:
			print("This request is not supported")
			print(raw_request)
			raise Exception
