import certifi
import urllib3
import asyncio
import aiohttp
import ipaddress
from torrent import Torrent
from bencode import Parser

class Tracker:
    def __init__(self, paras):
        self.URL = ""
        self.getURL(paras)
          
    def getURL(self, paras):
        URL = ''
        URL += paras['announce']
        URL += "?"
        URL += "info_hash="
        info_hash = paras["info_hash"]

        for index, _ in enumerate(info_hash):
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

    def get_peers(self):
        '''
        返回一个list, [[peer_ip, peer_id, peer_port], [peer_ip, peer_id, peer_port], ......]
        '''
        peers = []

        coroutine = self.http_request()
        loop = asyncio.get_event_loop()
        task = loop.create_task(coroutine)
        loop.run_until_complete(task)

        parser = Parser()
        result = parser.decode(task.result())

        #print(result[b'interval'])
        
        for item in result[b'peers']:
            ip = ipaddress.ip_address(bytes.decode(item[b'ip']))
            peers.append([ip, item[b'peer id'], item[b'port']])
        return peers
    

if __name__ == "__main__":
    torrent = Torrent('./test/ubuntu-18.04.5-desktop-amd64.iso.torrent')  
    tracker = Tracker(torrent.gen_request_paras())
    print(tracker.get_peers())
