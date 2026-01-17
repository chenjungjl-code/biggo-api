from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            
            # 直接抓取網頁內容
            req = urllib.request.Request(data.get('url', ''), headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', 'ignore')

            # 最原始、之前成功的抓取邏輯
            items = []
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                # 僅做最基本的 Unicode 還原，不做複雜解碼
                try:
                    name = n.encode().decode('unicode_escape')
                except:
                    name = n
                items.append({"title": name, "price": int(p), "shop": "BigGo"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
        except:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"[]")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Ready")