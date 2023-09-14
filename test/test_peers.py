import pytest

import socket

from py2p.peer import Peer

def test_peer_creation():
	peer = Peer()

	assert peer
	assert peer.alive == True

	peer.kill()

	assert peer.alive == False

def test_listener_creation():
	peer = Peer()

	assert peer.listener is not None
	assert peer.listener.type is socket.SOCK_STREAM

	peer.kill() 

	assert peer.alive == False