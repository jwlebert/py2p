import pytest

import socket
import time

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

    assert peer.listen_sock is not None
    assert peer.listen_sock.type is socket.SOCK_STREAM
    assert peer.listen_sock.getsockname() == peer.info.address

    peer.kill()

def test_connections():
    peer1 = Peer()
    peer2 = Peer()

    assert peer1.send_data(peer2.info, "Hello there!")
    
    for _ in range(50): #time buffer for transmission
        if len(peer2.transmissions) >= 1: break
        time.sleep(0.1)
    
    assert (peer1.info, 'READ', "Hello there!") in peer2.transmissions

    peer1.kill()
    peer2.kill()