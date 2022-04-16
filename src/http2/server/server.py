import socket

from .worker import Worker

class Server:
	def __init__(self, ip_addr:str, port:int, app):
		self.server_sock = socket.socket()
		self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_sock.bind((ip_addr,  port))
		self.app = app

	def serve(self):
		self.server_sock.listen(10)

		while True:
			client_sock, ip = self.server_sock.accept()
			worker = Worker(client_sock, self.app)
			print("Worker for {}:{} was started".format(ip[0], ip[1]))
			worker.start()

	def stop(self):
		self.server_sock.close()
			