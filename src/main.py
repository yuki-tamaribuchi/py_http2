from http2.server import Server

from http2.response import H2Response


def sample_app(request):
	print("***************************************************************************")
	print("app recieved request")
	print(request)
	print("***************************************************************************")
	options = {
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "ja",
		"Test-Field": "test"
	}
	if request.body:
		request_body = request.body
	else:
		request_body = b""
	response_body = b"Requested data: %s"%(request_body)
	response = H2Response(200, options, response_body)
	return response


if __name__ == "__main__":
	try:
		server = Server("127.0.0.1", 8000, sample_app)
		print("Server was started at http://127.0.0.1:8000")
		server.serve()

	except KeyboardInterrupt:
		server.stop()