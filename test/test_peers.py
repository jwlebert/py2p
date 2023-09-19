import pytest

import socket
import time

from py2p.peer import Peer, PeerInfo, IncomingConnection


def test_peer_creation():
    peer = Peer()

    assert peer
    assert peer.alive == True

    peer.kill()
    assert peer.alive == False

    info = PeerInfo(host="127.0.0.1", port=12001)
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
    peer1 = Peer(info=PeerInfo(port=12100))
    peer2 = Peer(info=PeerInfo(port=12101))

    assert peer1.send_data(peer2.info, "Hello there!")

    for _ in range(50):  # time buffer for transmission
        if len(peer2.transmissions) >= 1:
            break
        time.sleep(0.01)

    assert (
        IncomingConnection,
        peer1.info,
        "READ",
        "Hello there!",
    ) in peer2.transmissions

    assert peer1.send_data(peer2.info, "Nice to meet you!", instruction="MEET")

    for _ in range(50):
        if len(peer2.transmissions) >= 2:
            break
        time.sleep(0.01)

    assert (
        IncomingConnection,
        peer1.info,
        "MEET",
        "Nice to meet you!",
    ) in peer2.transmissions

    assert peer2.send_data(peer1.info, "Nice to meet you as well!", instruction="MEET")

    for _ in range(50):
        if len(peer1.transmissions) >= 3:
            break
        time.sleep(0.01)

    assert (
        IncomingConnection,
        peer2.info,
        "MEET",
        "Nice to meet you as well!",
    ) in peer1.transmissions

    peer1.kill()
    peer2.kill()
