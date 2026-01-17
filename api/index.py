from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            url = data.get('url', '')
            
            # 1. 抓取網頁
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw_data = response.read()
                html = raw_data.decode('utf-8', 'ignore')

            # 2. 嘗試抓取商品
            items = []
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                try:
                    name = n.encode().decode('unicode_escape')
                except:
                    name = n
                items.append({"title": name, "price": int(p), "shop": "BigGo"})

            # 3. 關鍵：如果抓不到商品，回傳網頁開頭供除錯
            if not items:
                debug_info = html[:500].replace('"', "'").replace("\n", " ")
                items.append({"title": f"DEBUG_FAIL: {debug_info}", "price": 0, "shop": "SYSTEM"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"ERROR: {str(e)}", "price": 0, "shop": "SYSTEM"}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Diagnostic System Ready")