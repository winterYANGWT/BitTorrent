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
        self.peers = []
        self.connections = []
        self.unfinished_blocks = []
        self.pieces = self.slice_to_pieces()
          
    def getURL(self, paras):
        URL = ''
        URL += paras['announce']
        URL += "?"
        URL += "info_hash="
        self.info_hash = paras["info_hash"]

        for index, _ in enumerate(self.info_hash.hex()):
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
        
        if not content:
            return None
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
        
        for piece in pieces:
            for block in piece.blocks:
                self.unfinished_blocks.append((piece.index, block.offset, block.length))
        return pieces
    
    async def download(self):
        last_update = 0
        tasks = []
        print("begin")

        #循环
        while True:
            tasks = []
            #如果下载完，退出
            if len(self.unfinished_blocks) == 0:
                break
            # if self.abort == 1:
            #     break
            cur_time = time.time()
            print("bbbb")

            #如果已经过了更新时间 或者 本轮结束
            if (last_update + self.interval < cur_time) or (len(self.peers) == 0) :
                #print("cccc")
                peers = await self.get_peers()
                if not peers:
                    continue
                self.peers = peers
                last_update = time.time()
                i = 0
                for peer in self.peers:
                    if i < len(self.unfinished_blocks):
                        index, offset, length = self.unfinished_blocks[i]
                        print("request:", index, offset, length)
                        i += 1
                        #print(i)
                        connection = Connection(str(peer[0]), peer[2], self.info_hash, self.torrent.gen_peer_id())
                        self.connections.append(connection)
                        task = asyncio.create_task(self.connections[-1].download_a_block(index, offset, length))
                        tasks.append(task)
                #print("start")
                results = await asyncio.gather(*tasks)
                #print("finish")
                for i, block in enumerate(results):
                    if block:
                        print("finished", block.index, block.offset, block.length)
                        try:
                            self.unfinished_blocks.remove((block.index, block.offset, block.length))
                            print("removed",block.index, block.offset, block.length)
                        except:
                            print("error", block.index, block.offset, block.length)
                self.peers = []
            else:
                await asyncio.sleep(1000)
        
if __name__ == "__main__":
    path = './test/ubuntu-20.10-desktop-amd64.iso.torrent'
    torrent = Torrent(path)
    tracker = Tracker(torrent)

    loop = asyncio.get_event_loop()
    task = loop.create_task(tracker.download())

    loop.run_until_complete(task)
   