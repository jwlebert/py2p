import socket
import random

from typing import Tuple

class PeerInfo:
	"""Represents the contact information of a peer on the network."""
	def __init__(self, host: str = '127.0.0.1', port: int = None):
		RAND_UP, RAND_LOW = 12000, 12100
		
		self.host: str = host
		self.port: int = port if port is not None else random.choice(range(RAND_UP, RAND_LOW))
	
	@property
	def address(self) -> Tuple[str, int]:
		return (self.host, self.port)
	
class Peer:
	"""Represents a peer on the peer to peer network."""
	alive: bool = True
	listener: socket.socket = None

	def __init__(self, info: PeerInfo = None):
		self.info: PeerInfo = info if info is not None else PeerInfo()
		self.start_listener()

	def start_listener(self, backlog: int = 5):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(self.info.address)
		s.listen(backlog)

		self.listener: socket.socket = s
	
	def kill(self):
		self.listener.close()

		self.alive = False