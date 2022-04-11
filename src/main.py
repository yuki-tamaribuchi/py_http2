from http2.server import Server


def sample_app(request):
	print("app recieved request")
	print(request)
	return


if __name__ == "__main__":
	try:
		server = Server("127.0.0.1", 8000, sample_app)
		print("Server was started at http://127.0.0.1:8000")
		server.serve()

	except KeyboardInterrupt:
		server.stop()