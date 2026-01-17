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
            
            # 強制導向台灣站點並設定較長等待時間
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            # 抓取 n 和 p 標籤 (BigGo 核心數據)
            items = []
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                # 去除 Unicode 編碼轉義
                try:
                    name = n.encode().decode('unicode_escape')
                except:
                    name = n.replace('\\', '')
                
                if len(name) > 3:
                    items.append({"title": name, "price": int(p), "shop": "BigGo"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": str(e), "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Ready")