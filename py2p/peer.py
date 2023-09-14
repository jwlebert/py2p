import socket

class Peer:
	alive: bool = True
	listener: socket.socket = None

	def __init__(self):
		self.start_listener(('127.0.0.1', 8080))

	def start_listener(self, addr, backlog=5):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(addr)
		s.listen(backlog)

		self.listener = s
	
	def kill(self):
		self.listener.close()

		self.alive = False
