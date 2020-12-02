import certifi
import urllib3
import asyncio
import aiohttp
import ipaddress
import time
from connection import Connection
from bencode import Parser
from torrent import Torrent
from block import Piece, Block

class Tracker:
    def __init__(self, torrent):
        self.torrent = torrent
        self.URL = ""
        self.info_hash = None
        self.getURL(self.torrent.gen_request_paras())   
        self.interval = 0
        self.connections = []
        self.unfinished_pieces = []
        self.finished_pieces = []
        self.pieces = self.slice_to_pieces()
        
          
    def getURL(self, paras):
        URL = ''
        URL += paras['announce']
        URL += "?"
        URL += "info_hash="
        self.info_hash = paras["info_hash"]

        for index, _ in enumerate(self.info_hash):
            if(index % 2 == 0):
                URL += '%'
            URL += _

        for key, value in paras.items():
            if (key != "announce" and key != "info_hash"):
                URL += "&" + key + "=" + str(value)
                
        self.URL = URL
    
    async def http_request(self):
        async with aiohttp.ClientSession() as session:
            r = await session.get(self.URL)
            content = await r.read()
            return content

    async def get_peers(self):
        '''
        返回一个list, [[peer_ip, peer_id, peer_port], [peer_ip, peer_id, peer_port], ......]
        '''
        peers = []

        content = await self.http_request()

        parser = Parser()
        result = parser.decode(content)
        
        print(result)
        self.interval = result[b'interval']

        for item in result[b'peers']:
            ip = ipaddress.ip_address(bytes.decode(item[b'ip']))
            peers.append([ip, item[b'peer id'], item[b'port']])

        return peers
    
    def slice_to_pieces(self):
        pieces = []
        file_length = self.torrent.info[b'length']
        piece_length = self.torrent.info[b'piece length']

        position = 0
        index = 0

        while position + piece_length < file_length:
            piece = Piece(index, length = piece_length)
            pieces.append(piece)
            position += piece_length
            index += 1
        
        if position < file_length:
            piece = Piece(index, length = file_length - position)
            pieces.append(piece)
            index += 1
        
        self.unfinished_pieces = [i for i in range(0, index)]
        self.finished_pieces = [0] * index
        return pieces
    
    # async def download(self):
    #     last_update = time.time()
    #     tasks = []

    #     while True:
    #         if len(self.unfinished_pieces) == 0:
    #             break
    #         if self.abort == 1:
    #             break
    #         cur_time = time.time()

    #         if last_update + self.interval < cur_time:
    #             self.peers = await self.get_peers()
    #             for peer in self.peers:
    #                 connection = Connection(peer[0], peer[2], self.info_hash, peer[1])
    #                 if connection.handshake == True:
    #                     self.connections.append(connection)
    #             根据peers生成connections
    #             调度算法，为每一个connection配备一个piece
    #             task.append(asyncio.create_task(一个协程,对应的connection下载一个piece))

    #             results = await asyncio.gather(*tasks)
    #             根据下好的piece更新self.
    #             self.unfinished_pieces.remove()
    #         else:
    #             await asyncio.sleep(1000)
        
if __name__ == "__main__":
    path = './test/ubuntu-20.10-desktop-amd64.iso.torrent'
    torrent = Torrent(path)
    tracker = Tracker(torrent)
    
    # loop = asyncio.get_event_loop()
    # task = loop.create_task(tracker.download())
    # try:
    #     loop.run_until_complete(task)
    # except CancelledError:
    #     logging.warning('Event loop was canceled')

