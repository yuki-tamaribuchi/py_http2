from http2.server import Server


if __name__ == "__main__":
	try:
		server = Server("127.0.0.1", 8000)
		print("Server was started at http://127.0.0.1:8000")
		server.serve()

	except KeyboardInterrupt:
		pass