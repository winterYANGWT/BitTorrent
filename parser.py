import json
import base64


class Parser(object):
    def __init__(self):
        super().__init__()
        self.decoder=Decoder()
        self.encoder=Encoder()

    def decode(self,bstr):
        return self.decoder.decode(bstr)

    def encode(self,data):
        return self.encoder.encode(data)


class Decoder(object):
    def __init__(self):
        super().__init__()

    def check_type(self,bstr):
        if bstr==b'i':
            return self.decode_int
        elif bstr==b'd':
            return self.decode_dict
        elif bstr==b'l':
            return self.decode_list
        elif bstr in b'0123456789':
            return self.decode_string

    def decode(self,bstr):
        '''
        convert bstr to bstr
        '''
        result,length=self.check_type(bstr[0:1])(bstr,0)
        return result

    def decode_int(self,bstr,f):
        f+=1
        newf=bstr.index(b'e',f)
        integer=int(bstr[f:newf])
    
        return integer,newf+1

    def decode_string(self,bstr,f):
        colon=bstr.index(b':',f)
        length=int(bstr[f:colon])
        string=bstr[colon+1:colon+length+1]

        return string,colon+length+1

    def decode_list(self,bstr,f):
        f+=1
        l=[]
        
        while bstr[f:f+1]!=b'e':
            item,f=self.check_type(bstr[f:f+1])(bstr,f)
            l.append(item)

        return l,f+1

    def decode_dict(self,bstr,f):
        f+=1
        d={}

        while bstr[f:f+1]!=b'e':
            key,f=self.decode_string(bstr,f)
            value,f=self.check_type(bstr[f:f+1])(bstr,f)
            d[key]=value

        return d,f+1


class Encoder(object):
    def __init__(self):
        super().__init__()

    def encode(self,data):
        bstr=self.check_type(data)(data)
        return bstr

    def check_type(self,data):
        if type(data) is int:
            return self.encode_int
        elif type(data) is bytes:
            return self.encode_string
        elif type(data) is list:
            return self.encode_list
        elif type(data) is dict:
            return self.encode_dict

    def encode_int(self,data): 
        bstr=bytes('i{}e'.format(str(data)),encoding='utf8')
        return bstr

    def encode_string(self,data):
        bstr=bytes('{}:'.format(len(data)),encoding='utf8')+data
        return bstr

    def encode_list(self,data):
        bstr=b'l'

        for item in data:
            bstr+=self.check_type(item)(item)

        bstr+=b'e'
        return bstr

    def encode_dict(self,data):
        bstr=b'd'

        for key,value in data.items():
            bstr+=self.check_type(key)(key)
            bstr+=self.check_type(value)(value)

        bstr+=b'e'
        return bstr

            
if __name__ == '__main__':
    with open('./test/ubuntu-20.10-desktop-amd64.iso.torrent','rb') as f:
        dec=Parser()
        bstr=f.read()
        d=dec.decode(bstr)
        b=dec.encode(d)
        print(b==bstr)