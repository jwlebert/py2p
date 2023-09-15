import socket
import random

from threading import Thread
from typing import Tuple

class PeerInfo:
	"""Represents the contact information of a peer on the network."""
	def __init__(self, host: str = '127.0.0.1', port: int = None, addr: Tuple[str, int] = None):
		RAND_UP, RAND_LOW = 12000, 12100

		if addr != None:
			self.host = addr[0]
			self.port = addr[1]
			return
		
		self.host: str = host
		self.port: int = port if port is not None else random.choice(range(RAND_UP, RAND_LOW))
	
	@property
	def address(self) -> Tuple[str, int]:
		return (self.host, self.port)
	
class PeerConnection:
	def __init__(self, socket: socket.socket, info: PeerInfo) -> None:
		self.socket: socket.socket = socket
		self.info: PeerInfo = info

	def send(self, data, command = 'READ') -> bool:
		pass

	def recv(self) -> Tuple[str, str]:
		pass

	def __pack_data(self, data):
		pass

	def __unpack_data(self, data):
		pass

	def close(self):
		self.send("END OF TRANSMISSION")

		self.socket.close()

class IncomingConnection(PeerConnection):
	def __init__(self, socket: socket.socket, info: PeerInfo) -> None:
		PeerConnection.__init__(self, socket, info)
	
class OutgoingConnection(PeerConnection):
	def __init__(self, info: PeerInfo) -> None:
		self.info: PeerInfo = info

		self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(self.info.address)

class Peer:
	"""Represents a peer on the peer to peer network."""
	alive: bool = True
	listen_sock: socket.socket = None

	def __init__(self, info: PeerInfo = None) -> None:
		self.info: PeerInfo = info if info is not None else PeerInfo()
		self.start_listener()

	def start_listener(self, backlog: int = 5) -> None:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(self.info.address)
		s.listen(backlog)

		self.listen_sock: socket.socket = s

		self.listener: Thread = Thread(target = self.await_connection)
		self.listener.start()

	def await_connection(self) -> None:
		sock, addr = self.listen_sock.accept()
		sock.settimeout(120)

		info = PeerInfo(addr=addr)

		connection = IncomingConnection(sock, info)

		t = Thread(target = self.handle_connection, args = [connection])

	def handle_connection(self, connection: IncomingConnection) -> None:
		command, data = connection.recv()
		
	
	def kill(self) -> None:
		self.listen_sock.close()

		self.alive = False