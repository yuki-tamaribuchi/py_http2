status_dict = {
	"101": "101 Switching Protocols",
	"200": "200 OK"
}

class Response:
	def __init__(self, version:str, status:int, options:dict=None, body:bytes=None):
		if not str(status) in status_dict:
			print("Please add status code %d to status_dict"%(status))
			raise Exception
		
		self.version = version
		self.status = status_dict[str(status)]
		self.options = options
		self.body = body

	def get_raw_response(self):
		raw_response = b""

		raw_response += bytes("%s %s\r\n"%(self.version ,self.status), "ascii")

		if self.options:
			for k, v in self.options.items():
				k = bytes(k, "ascii")
				v = bytes(v, "ascii")
				raw_response += b"%s: %s\r\n"%(k, v)
		raw_response += b"\r\n"

		if self.body:
			raw_response += self.body+b"\r\n"

		return raw_response