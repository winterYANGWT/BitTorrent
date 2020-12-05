
BLOCKSIZE = 2**14

class Piece:
    def __init__(self, index, length):
        self.index = index
        self.length = length
        self.info_hash = b''

        self.blocks = []
        # self.finished_blocks = []   #[0, 0 ,0 ,0, 0, 0]
        # self.unfinished_blocks = [] #[0, 1, 2, 3, 4, 5]      
        self.complete = False
        self.slice_to_blocks()

    def slice_to_blocks(self):
        offset = 0
        index = 0
        while(offset + BLOCKSIZE < self.length):
            block = Block(index, offset, length = BLOCKSIZE)
            self.blocks.append(block)
            offset += BLOCKSIZE
            index += 1
            
        if(offset < self.length):
            block = Block(self.index, offset, length = (self.length - offset))
            self.blocks.append(block)
            index += 1
        
        self.unfinished_blocks = [i for i in range(0, index)]
        self.finished_blocks = [0] * index
    
    def check_hash(self, hash):
        pass
    

class Block:
    def __init__(self, index, offset, length):
        self.index = index
        self.offset = offset
        self.length = length
        self.content = None

