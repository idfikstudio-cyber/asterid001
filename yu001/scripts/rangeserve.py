# Static file server with HTTP Range support (Chrome needs it to seek <video>)
import http.server,os,re,sys
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a):pass
    def send_head(self):
        p=self.translate_path(self.path);rng=self.headers.get("Range")
        if not rng or not os.path.isfile(p):return super().send_head()
        size=os.path.getsize(p);m=re.match(r"bytes=(\d*)-(\d*)",rng);a=int(m[1] or 0);b=int(m[2]) if m[2] else size-1;b=min(b,size-1)
        f=open(p,"rb");f.seek(a);self.send_response(206);self.send_header("Content-Type",self.guess_type(p))
        self.send_header("Accept-Ranges","bytes");self.send_header("Content-Range",f"bytes {a}-{b}/{size}");self.send_header("Content-Length",str(b-a+1));self.end_headers()
        self.rlen=b-a+1;return f
    def copyfile(self,src,dst):
        n=getattr(self,"rlen",None)
        if n is None:return super().copyfile(src,dst)
        while n>0:
            c=src.read(min(1<<20,n))
            if not c:break
            dst.write(c);n-=len(c)
os.chdir(sys.argv[1]);http.server.ThreadingHTTPServer(("127.0.0.1",int(sys.argv[2])),H).serve_forever()
