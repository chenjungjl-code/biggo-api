from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            html = data.get('html', '')
            
            # 解碼 Unicode
            try:
                html = html.encode().decode('unicode_escape', 'ignore')
            except:
                pass

            # 搜尋 BigGo 專屬的商品區塊 (n:品名, p:價格)
            # 使用更靈活的正則，允許中間有更多雜訊
            items = []
            pattern = r'"n"\s*:\s*"([^"]+?)"\s*,\s*"p"\s*:\s*(\d+)'
            matches = re.findall(pattern, html, re.S)
            
            for n, p in matches:
                if len(n) > 5:
                    items.append({"title": n, "price": int(p), "shop": "BigGo比價"})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scraper Ready.")