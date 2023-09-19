import socket
import struct
import random

from threading import Thread
from typing import Tuple, List

from py2p.listener import Listener

class PeerInfo:
    """Represents the contact information of a peer on the network."""
    def __init__(self, host: str = '127.0.0.1', port: int = None, addr: Tuple[str, int] = None):
        RAND_UP, RAND_LOW = 12000, 12500

        if addr != None:
            self.host = addr[0]
            self.port = addr[1]
            return
        
        self.host: str = host
        self.port: int = port if port is not None else random.choice(range(RAND_UP, RAND_LOW))
        self.owner: Peer = None
    
    @property
    def address(self) -> Tuple[str, int]:
        return (self.host, self.port)
    
    def __eq__(self, other):
        if isinstance(other, PeerInfo):
            return self.host == other.host and \
                self.port == other.port and \
                self.address == other.address
        return NotImplemented

    
class PeerConnection:
    socket: socket.socket
    info: PeerInfo

    def __init__(self) -> None:
        self.data: socket.SocketIO = self.socket.makefile('rwb', 0)

    def close(self):
        self.socket.close()

class IncomingConnection(PeerConnection):
    def __init__(self, sock: socket.socket) -> None:
        self.socket: socket.socket = sock
        self.info: PeerInfo = None

        PeerConnection.__init__(self)
    
    def recv(self) -> Tuple[str, str]:
        try:
            instruction = self.data.read(4).decode("utf-8")
            if not instruction: raise ValueError("No instruction")

            data = self.data.read(4)
            msg_len = struct.unpack("!I", data)[0]
            if not msg_len: raise ValueError("No message length")

            data = ""

            while len(data) != msg_len:
                d = self.data.read(min(2048, msg_len - len(data)))
                # read either 2048 bytes or the remaining amount of data,
                # whichever is smaller
                if not len(d): break
                data += d.decode("utf-8")
            
            if len(data) != msg_len:
                raise Exception("length of data received is not same as supposed message length")
            
            host_len = struct.unpack("!I", self.data.read(4))[0]
            if host_len:
                host = self.data.read(host_len).decode('utf-8')
                port = struct.unpack("!I", self.data.read(4))[0]

            if (host, port) != ('NO_RET_ADDR', 0):
                self.info = PeerInfo(host=host, port=port)
            else:
                raise Exception("NO RETURN ADDRESS")

        except Exception as e:
            print(e)
            self.close()
            return None
        
        self.close()
        return (instruction, data)
    
class OutgoingConnection(PeerConnection):
    def __init__(self, info: PeerInfo) -> None:
        self.info: PeerInfo = info

        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.info.address)

        PeerConnection.__init__(self)
    
    def send(self, data, instruction = 'READ', ret_addr = None) -> bool:
        try:
            instruction = instruction.encode('utf-8')
            msg = data.encode('utf-8')

            host, port = 'NO_RET_ADDR', 0
            if ret_addr is not None:
                host, port = ret_addr
                
            host = host.encode('utf-8')

            data = struct.pack("!4sI%dsI%dsI" % (len(msg), len(host)), instruction, len(msg), msg, len(host), host, port)
            # "!4sL%ds" is the format that we are packing to
            # !     ->  bite order, size, alignment
            # 4s    ->  a string of 4 characters
            # I     ->  an unsigned int (4 byte number, with no sign (+/-))
            # %ds   ->  a string of length %d, where d is replaced by what follows
            #           the '%' after the format (in this case, len(msg))
            
            self.data.write(data)
            self.close()
            return True
        except Exception as e:
            print(e)
            self.close()
            return False

class Peer:
    """Represents a peer on the peer to peer network."""
    alive: bool = True
    listen_sock: socket.socket = None
    transmissions: List[Tuple[PeerConnection, PeerInfo, str, str]]

    def __init__(self, info: PeerInfo = None) -> None:
        self.info: PeerInfo = info if info is not None else PeerInfo()
        self.transmissions = []
        self.info.owner = self;
        self.start_listener()

    def start_listener(self, backlog: int = 5, timeout: int = 5) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(self.info.address)
        s.listen(backlog)

        self.listen_sock: socket.socket = s

        self.listener: Listener = Listener(target = self.await_connection)
        self.listener.start()

    def await_connection(self) -> None:
        while self.alive:
            sock, addr = self.listen_sock.accept()

            connection = IncomingConnection(sock)
            t = Thread(target = self.handle_connection, args = [connection])
            t.start()

    def handle_connection(self, connection: IncomingConnection) -> None:
        recv = connection.recv()
        if recv == None:
            raise

        # do stuff

        self.transmissions.append((IncomingConnection, connection.info, *recv))

    def send_data(self, target: PeerInfo, data, instruction = 'READ') -> bool:
        try:
            connection = OutgoingConnection(target)
            if connection.send(data, instruction = instruction, ret_addr = self.info.address):
                self.transmissions.append((OutgoingConnection, target, instruction, data))
                return True
        except Exception as e:
            print(e)
            return False
    
    def kill(self) -> None:
        self.listener.close()
        if self.listener.alive:
            self.listener.join(5)
        self.listen_sock.close()

        self.alive = False