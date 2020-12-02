import struct
from bitstring import BitArray

KEEPALIVE = -1
CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
NOTINTERESTED = 3
HAVE = 4
BITFIELD = 5
REQUEST = 6
PIECE = 7
CANCEL = 8
HANDSHAKE = 9

class Message:
    def __init__(self, typeID):
        self.typeID = typeID

    def gen_string(self):
        pass

class KeepAliveMessage(Message):
    def __init__(self):
        super().__init__(KEEPALIVE)

    def gen_string(self):
        return b'0000'

class StateMessage(Message):
    def __init__(self, typeID):
        super().__init__(typeID)
        self.len = 1

    def gen_string(self):
        return struct.pack('>Ib', self.len, self.typeID)


class HaveMessage(Message):
    def __init__(self, typeID, index):
        super().__init__(typeID)
        self.len = 5
        self.index = index

    def gen_string(self):
        return struct.pack('>IbI',self.len, self.typeID, self.index)


class BitFieldMessage(Message):
    '''
    bitfield是bytes型
    '''
    def __init__(self, typeID, bitfield):
        super().__init__(typeID)
        self.len = 1 + len(bitfield)
        self.bitfield = bitfield
        self.bitarray = BitArray(self.bitfield)

    def gen_string(self):
        return struct.pack('>Ib', self.len, self.typeID) + self.bitfield


class RequestMessage(Message):
    def __init__(self, typeID, index, begin, length):
        super().__init__(typeID)
        self.len = 13
        self.index = index
        self.begin = begin
        self.length = length

    def gen_string(self):
        return struct.pack('>IbIII', self.len, self.typeID, self.index, self.begin, self.length)


class PieceMessage(Message):
    def __init__(self, typeID, index, begin, content):
        super().__init__(typeID)
        self.len = 9 + len(content)
        self.index = index
        self.begin = begin
        self.content = content

    def gen_string(self):
        return struct.pack('>IbIII', self.len, self.typeID, self.index, self.begin, self.content)


class CancelMessage(Message):
    def __init__(self, typeID, index, begin, length):
        super().__init__(typeID)
        self.len = 13
        self.index = index
        self.begin = begin
        self.length = length

    def gen_string(self):
        return struct.pack('>IbIII', self.len, self.typeID, self.index, self.begin, self.length)

class HandShakeMessage(Message):
    def __init__(self, typeID, info_hash, peer_id, pstr = b'BitTorrent protocol'):
        super().__init__(typeID)
        self.pstr = pstr
        self.info_hash = info_hash
        self.peer_id = peer_id
    
    def gen_string(self):
        return b'' + '19'.encode() + b'BitTorrent protocol' + '00000000'.encode() + self.info_hash.encode() + self.peer_id





