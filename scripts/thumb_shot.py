import functools,http.server,threading,sys
from playwright.sync_api import sync_playwright
D=sys.argv[1]
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
s=http.server.ThreadingHTTPServer(("127.0.0.1",8797),functools.partial(Q,directory=D));threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome");pg=b.new_page(viewport={"width":1080,"height":1920})
    for v in ("1","2"):
        pg.goto(f"http://127.0.0.1:8797/thumb.html?v={v}");pg.wait_for_load_state("networkidle");pg.evaluate("document.fonts.ready");pg.wait_for_timeout(500)
        pg.screenshot(path=f"{D}/thumb{v}.png")
