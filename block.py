
BLOCKSIZE = 2**14

class Piece:
    def __init__(self, index, length):
        self.index = index
        self.length = length
        self.info_hash = b''

        self.blocks = []
        self.downloaded_blocks = []
        
        self.complete = False
        self.slice_to_blocks()

    def slice_to_blocks(self):
        offset = 0
        while(offset + BLOCKSIZE < self.length):
            block = Block(self.index, offset, length = BLOCKSIZE)
            self.blocks.append(block)
            offset += BLOCKSIZE
        
        if(offset < self.length):
            block = Block(self.index, offset, length = (self.length - offset))
            self.blocks.append(block)
    
    def download_a_block(self):
        pass


    def check_hash(self, hash):
        pass
    

class Block:
    def __init__(self, index, offset, length):
        self.index = index
        self.offset = offset
        self.length = length
        self.content = None

