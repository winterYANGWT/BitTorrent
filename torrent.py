import random
import string
from hashlib import sha1
from bencode import Parser 

class Torrent:
    def __init__(self, path):
        self.filepath = path
        self.parser = Parser()
        self.raw_content = ''
        self.torrent_dict = {}
        self.announce = ""
        self.announce_list = []
        self.name = ""
        self.info = {}
        self.files = {}
        self.is_multi_file = False
        self.get_value()


    def get_value(self):
        with open(self.filepath, 'rb') as f:
            self.raw_content = f.read()
            
        self.torrent_dict = self.parser.decode(self.raw_content)

        if self.torrent_dict.get(b'announce_list') is not None :
            self.announce_list = self.torrent_dict[b'announce_list']

        if self.torrent_dict.get(b'announce') is None :
            self.announce = self.torrent_dict[b'announce-list'][0][0]
        else:
             self.announce = self.torrent_dict[b'announce']

        self.info = self.torrent_dict[b'info']

        if self.info.get(b'files') is not None:
            self.is_multi_file = True
            self.files = self.info[b'files']

        print(self.announce)

    def gen_request_paras(self):
        '''
        genearte tracker request parameters

        Returns:
            paras : a dictionary containing parameters of tracker request
        '''
        paras={}

        paras["announce"] = bytes.decode(self.announce)
        paras["info_hash"] =sha1(self.parser.encode(self.info)).hexdigest()
        paras["peer_id"] = self.gen_peer_id()
        paras["port"] = "6881"
        paras["uploaded"] = "0"
        paras["downloaded"] = "0"
        paras["left"] = self.info[b'length']
        paras["event"] = "started"

        print(paras)

        return paras

    def gen_peer_id(self):
        prefix = "DSproject"
        random_str = ''.join(random.sample(string.ascii_letters + string.digits,11))
        return prefix + random_str

    def get_pieces_hashes(self):
        '''
        get hashes of pieces

        Returns:
            a list containing hashes of every piece 
        '''
        pieces = self.info[b"pieces"]
        hashes = [pieces[i:i+20] for i in range(0, len(pieces), 20)]
        return hashes


if __name__ == "__main__":
    torrent = Torrent('./test/ubuntu-20.10-desktop-amd64.iso.torrent')  
    torrent.gen_request_paras()
