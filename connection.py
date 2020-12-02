import asyncio
from block import Block, Piece
from message import *

class Connection:
    def __init__(self, ip, port, info_hash, peer_id):
        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        self.peer_id = peer_id

        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0

        self.available_pieces = []
        self.bytes_stream = b''

        self.piece = None
        self.reader = None
        self.writer = None


    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)

    async def handshake(self):
        #await self.connect()
        message = HandShakeMessage(HANDSHAKE, self.info_hash, self.peer_id)
        print(message.gen_string())
        return 
        await self.write(message.gen_string())
        message = await self.read_a_message()
        if message.typeID == HANDSHAKE:
            return True
        else:
            return False

    async def read_a_message(self):
        while(len(self.bytes_stream) < 4):
                await self.read()

        if self.bytes_stream[0:4] == b'\x13Bit':
            while(len(self.bytes_stream) < 68):
                await self.read()  
            pstr = self.bytes_stream[0:20]
            info_hash = self.bytes_stream[28:48]
            peer_id = self.bytes_stream[48:68]
            message = HandShakeMessage(HANDSHAKE, info_hash, peer_id, pstr)
            self.bytes_stream = self.bytes_stream[68:]
            return message

        if self.bytes_stream[0:4] == b'0000':
            self.bytes_stream = self.bytes_stream[4:]
            return KeepAliveMessage()

        message_length = struct.unpack('>I', self.bytes_stream[0:4])
        while(len(self.bytes_stream) < 4 + message_length):
            await self.read()
        
        type_ID = int(self.bytes_stream[5])

        if type_ID in [CHOKE, UNCHOKE, INTERESTED, NOTINTERESTED]:
            self.bytes_stream = self.bytes_stream[5:]
            return StateMessage(type_ID)

        if type_ID == HaveMessage:
            index = struct.unpack('>I', self.bytes_stream[5:9])[0]
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return HaveMessage(type_ID, index)
        
        if type_ID == BITFIELD:
            bitfield = self.bytes_stream[5:message_length+4]
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return BitFieldMessage(type_ID, bitfield)

        if type_ID == REQUEST:
            index, begin, length = struct.unpack('>III', self.bytes_stream[5:17])
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return RequestMessage(type_ID, index, begin, length)
            
        if type_ID == PIECE:
            index, begin = struct.unpack('>II', self.bytes_stream[5:13]) 
            block = self.bytes_stream[13:message_length+4]
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return PieceMessage(type_ID, index, begin, block)

        if type_ID == CANCEL:
            index, begin, length = struct.unpack(">III", self.bytes_stream[5:17])
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return CancelMessage(type_ID, index, begin, length)

    # async def read_messages(self):
    #     messages = []
    #     bytes_stream = b''

    #     while(True):
    #         bytes_stream += await self.reader.read(1024)

    #         if(len(bytes_stream) < 5):
    #             continue

    #         if bytes_stream[0:4] == b'\x13BitT':
    #             if(len(bytes_stream) < 68):
    #                 continue
    #             else:
    #                 handshakemessage = bytes_stream[0:68]
    #                 pstr = handshakemessage[0:20]
    #                 info_hash = handshakemessage[28:48]
    #                 peer_id = handshakemessage[48:68]
    #                 message = HandShakeMessage(HANDSHAKE, info_hash, peer_id, pstr)
    #                 messages.append(message)
    #                 bytes_stream = bytes_stream[68:]
            
    #         if bytes_stream[0:4] == b'0000':
    #             message = KeepAliveMessage()
    #             messages.append(message)
    #             bytes_stream = bytes_stream[4:]

    #         message_length = struct.unpack('>I', bytes_stream[0:4])[0]

    #         if len(bytes_stream) < message_length + 4:
    #             continue

    #         type_ID = int(bytes_stream[5])

    #         if type_ID in [CHOKE, UNCHOKE, INTERESTED, NOTINTERESTED]:
    #             message = StateMessage(type_ID)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[5:]
    #             continue

    #         if type_ID == HaveMessage:
    #             index = struct.unpack('>I', bytes_stream[5:9])[0]
    #             message = HaveMessage(type_ID, index)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[message_length+4:]
    #             continue
            
    #         if type_ID == BITFIELD:
    #             bitfield = bytes_stream[5:message_length+4]
    #             message = BitFieldMessage(type_ID, bitfield)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[message_length+4:]
    #             continue

    #         if type_ID == REQUEST:
    #             index, begin, length = struct.unpack('>III', bytes_stream[5:17])
    #             message = RequestMessage(type_ID, index, begin, length)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[message_length+4:]
    #             continue
                
    #         if type_ID == PIECE:
    #             index, begin = struct.unpack('>II', bytes_stream[5:13]) 
    #             block = bytes_stream[13:message_length+4]
    #             message = PieceMessage(type_ID, index, begin, block)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[message_length+4:]
    #             continue

    #         if type_ID == CANCEL:
    #             index, begin, length = struct.unpack(">III", bytes_stream[5:17])
    #             message = CancelMessage(type_ID, index, begin, length)
    #             messages.append(message)
    #             bytes_stream = bytes_stream[message_length+4:]
        
    #     return messages

    async def scan_messages(self, messages):
        num = len(messages)

        while num>0:
            message = messages[0]
            typeID = message.typeID

            if typeID == KEEPALIVE:
                continue
            
            if typeID == CHOKE:
                self.peer_choking = 1
            
            if typeID == UNCHOKE:
                self.peer_choking = 0

            # if typeID == INTERESTED:
            #     self.peer_interested = 1
            
            # if typeID == NOTINTERESTED:
            #     self.peer_interested = 0
            
            if typeID == HAVE:
                self.available_pieces.append(message.index)

            if typeID == BITFIELD:
                bitarray = message.bitarray
                for i in range(len(message.bitarray)):
                    if bitarray[i]:
                        self.available_pieces.append(i)

            if typeID == REQUEST:
                pass

            if typeID == PIECE:
                for block in self.piece.blocks:
                    if block.offset == message.begin:
                        block.content = message.content
                        self.piece.downloaded_blocks.append[block]
                        if len(self.piece.downloaded_blocks) == len(self.piece.blocks):
                            self.piece

            if typeID == CANCEL:
                pass

            if typeID == HANDSHAKE:
                if(message.pstr != b'\x13BitTorrent protocol' 
                    and message.info_hash != self.info_hash 
                    and message.peer_id != self.peer_id):
                    self.close()


    async def download(self, index, length):
        self.piece = Piece(index, length)
        for block in self.piece.undownload_blocks:
            message = RequestMessage(REQUEST, index, block.offset, block.length)
            self.write(message.gen_string())

    async def write(self, bytes_string):
        self.writer.write(bytes_string)

    async def read(self, length = 1024):
        self.bytes_stream += await self.reader.read(length)

    def close(self):
        self.writer.close()

if __name__ == "__main__":
    from tracker import Tracker
    from torrent import Torrent
    path = './test/ubuntu-20.10-desktop-amd64.iso.torrent'
    torrent = Torrent(path)
    tracker = Tracker(torrent)
    
    loop = asyncio.get_event_loop()
    task = loop.create_task(tracker.get_peers())
    loop.run_until_complete(task)
    peers = task.result()
    peer = peers[0]
    
    print(peers)
    print(tracker.info_hash)

    # connection = Connection(str(peer[0]), peer[2], tracker.info_hash, peer[1])
    # task = loop.create_task(connection.handshake())
    # loop.run_until_complete(task)
    # print(task.result()) 