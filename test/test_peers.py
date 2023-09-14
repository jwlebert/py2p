import pytest

import socket

from py2p.peer import Peer, PeerInfo

def test_peer_creation():
	peer = Peer()

	assert peer
	assert peer.alive == True

	peer.kill()
	assert peer.alive == False

	info = PeerInfo(host='127.0.0.1', port=12001)
	peer = Peer(info=info)

	assert peer.info == info
	assert peer.info.host == info.host
	assert peer.info.port == info.port
	assert peer.info.address == info.address

	peer.kill()
	assert peer.alive == False

def test_listener_creation():
	peer = Peer()

	assert peer.listener is not None
	assert peer.listener.type is socket.SOCK_STREAM
	assert peer.listener.getsockname() == peer.info.address

	peer.kill()