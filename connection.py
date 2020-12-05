import asyncio
from block import Block, Piece
from message import *

class Connection:
    def __init__(self, ip, port, info_hash, my_id):
        self.ip = ip
        self.port = port
        self.info_hash = info_hash
        if(type(my_id) == bytes):
            self.my_id = my_id
        if(type(my_id) == str):
            self.my_id = my_id.encode()
        self.am_choking = 1
        self.am_interested = 0
        self.peer_choking = 1
        self.peer_interested = 0

        self.handshake_sucess = False
        self.download_sucess = False

        self.available_pieces = []
        self.bytes_stream = b''

        self.block = None

        self.reader = None
        self.writer = None


    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            return 1
        except Exception as e:
            print("Failed to connect")
            return 0

    async def handshake(self):
        
        #print("in handshake")
        messages = []
        state = await self.connect()
        if state == 0:
            return False
        message = HandShakeMessage(HANDSHAKE, self.info_hash, self.my_id)
        await self.write(message.gen_string())
        try:
            message = await self.read_a_message()
        except:
            return False
        while message != None and message.typeID != KEEPALIVE:
            messages.append(message)
            message = await self.read_a_message()
        for message in messages:
            #print("message:"+str(message.typeID))
            self.handle_message(message)
        if self.handshake_sucess == 1:
            return True
        return False

    async def read_a_message(self):
        while(len(self.bytes_stream) < 4):
            data = await self.read()
            if len(data) == 0:
                return None
            self.bytes_stream += data

        if self.bytes_stream[0:4] == b'\x13Bit':
            while(len(self.bytes_stream) < 68):
                self.bytes_stream += await self.read()  
            pstr = self.bytes_stream[0:20]
            info_hash = self.bytes_stream[28:48]
            my_id = self.bytes_stream[48:68]
            message = HandShakeMessage(HANDSHAKE, info_hash, my_id, pstr)
            self.bytes_stream = self.bytes_stream[68:]
            return message

        if self.bytes_stream[0:4] == b'\x00\x00\x00\x00':
            self.bytes_stream = self.bytes_stream[4:]
            return KeepAliveMessage()

        message_length = struct.unpack('>I', self.bytes_stream[0:4])[0]
        while(len(self.bytes_stream) < 4 + message_length):
            #print(len(self.bytes_stream))
            data = await self.read()
            self.bytes_stream += data
        
        type_ID = int(self.bytes_stream[4])

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

        if type_ID == EXTENSION:
            info = self.bytes_stream[5:message_length+4]
            self.bytes_stream = self.bytes_stream[message_length+4:]
            return ExtensionMessage(type_ID, info)

    def handle_message(self, message):

        typeID = message.typeID

        if typeID == KEEPALIVE:
            return
        
        if typeID == CHOKE:
            self.am_choking = 1
        
        if typeID == UNCHOKE:
            self.am_choking = 0

        if typeID == INTERESTED:
            self.am_interested = 1
        
        if typeID == NOTINTERESTED:
            self.am_interested = 0
        
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
            self.block = Block(message.index, message.begin, len(message.content))
            self.block.content = message.content

        if typeID == CANCEL:
            pass

        if typeID == HANDSHAKE:
            if(message.pstr != b'\x13BitTorrent protocol' 
                and message.info_hash != self.info_hash 
                and message.my_id != self.my_id):
                self.close()
            else:
                self.handshake_sucess = 1


    async def download_a_block(self, index, offset, length):
        try:
            #print("in download")
            await self.handshake()
            if self.handshake_sucess == 0:
                return self.block
            messages = []
            message = StateMessage(INTERESTED)
            await self.write(message.gen_string())
            await asyncio.sleep(5)
            message = await self.read_a_message()
            while message != None and message.typeID != KEEPALIVE:
                messages.append(message)
                message = await self.read_a_message()
            for message in messages:
                #print("message:"+str(message.typeID))
                self.handle_message(message)

            if self.am_choking == 1:
                return self.block
            message = RequestMessage(REQUEST, index, offset, length)
            await self.write(message.gen_string())
        
            for i in range(10):       
                #print("123")
                message = await self.read_a_message()
                # if(message == None):
                #     return self.block
                #print("456")
                while(message != None and self.download_sucess == False) :
                    #print("789")
                    #print("message123:",message.typeID)
                    self.handle_message(message)
                    if(message.typeID == PIECE):
                        #print("piece")
                        self.download_sucess = True
                        return self.block
                    message = await self.read_a_message() 
        except:
            return self.block

    async def write(self, bytes_string):
        self.writer.write(bytes_string)

    async def read(self, length = 1024, timeout = 1):
        try:
            data = await asyncio.wait_for(self.reader.read(length), timeout)
            return data
        except asyncio.TimeoutError as e:
            return b''

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
    print("1")
    connection = Connection(str(peer[0]), peer[2], tracker.info_hash, b'qwertyuiopasdfghjklz')
    task = loop.create_task(connection.download_a_block(0, 0, 16348))
    loop.run_until_complete(task)
    print("3")
    if connection.block != None:
        print(connection.block.content)