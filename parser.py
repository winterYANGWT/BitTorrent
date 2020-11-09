import json
import base64


class Parser(object):
    def __init__(self):
        super().__init__()
        self.decode_func={}
        self.decode_func[b'i']=self.decode_int
        self.decode_func[b'd']=self.decode_dict
        self.decode_func[b'l']=self.decode_list
        self.decode_func[b'0']=self.decode_string
        self.decode_func[b'1']=self.decode_string
        self.decode_func[b'2']=self.decode_string
        self.decode_func[b'3']=self.decode_string
        self.decode_func[b'4']=self.decode_string
        self.decode_func[b'5']=self.decode_string
        self.decode_func[b'6']=self.decode_string
        self.decode_func[b'7']=self.decode_string
        self.decode_func[b'8']=self.decode_string
        self.decode_func[b'9']=self.decode_string

    def decode(self,file_path):
        with open(file_path,'rb') as f:
            bstr=f.read()

        result,length=self.decode_func[bstr[0:1]](bstr,0)

        with open('result.json','w') as f:
            json.dump(result,f,indent=4)

    def decode_int(self,bstr,f):
        f+=1
        newf=bstr.index(b'e',f)
        integer=int(bstr[f:newf])
    
        return integer,newf+1

    def decode_string(self,bstr,f):
        colon=bstr.index(b':',f)
        length=int(bstr[f:colon])
        string=str(bstr[colon+1:colon+length+1])

        return string,colon+length+1

    def decode_list(self,bstr,f):
        f+=1
        l=[]
        
        while bstr[f:f+1]!=b'e':
            item,f=self.decode_func[bstr[f:f+1]](bstr,f)
            l.append(item)

        return l,f+1

    def decode_dict(self,bstr,f):
        f+=1
        d={}

        while bstr[f:f+1]!=b'e':
            key,f=self.decode_string(bstr,f)
            value,f=self.decode_func[bstr[f:f+1]](bstr,f)
            d[key]=value

        return d,f+1

if __name__ == '__main__':
    dec=Parser()
    d=dec.decode('ubuntu.torrent')

