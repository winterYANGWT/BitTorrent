import random
import string
from hashlib import sha1

class Torrent:
    def __init__(self, path):
        self.filepath = path
        self.torrent_dict = {}
        self.announce = ""
        self.announce_list = []
        self.info = {}

    def get_value(self):
        self.torrent_dict = decode(filepath)
        self.announce = self.torrent_dict[b"announce"]
        if self.torrent_dict.get(b"announce_list") is not None :
            self.announce_list = self.torrent_dict[b"announce_list"]
        self.info = self.torrent_dict[b"info"]

    def gen_request_paras(self):
        '''
        genearte tracker request parameters

        Returns:
            paras : a dictionary containing parameters of tracker request
        '''
        paras={}

        #bencode?
        paras["info_hash"] =sha1(bencode(self.info)).digest()
        paras["peer_id"] = self.gen_peer_id()
        paras["port"] = "6881"
        paras["uploaded"] = "0"
        paras["downloaded"] = "0"
        paras["left"] = self.info[b'length']
        paras["event"] = "started"
        #paras["numwant"] = "" 

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


    