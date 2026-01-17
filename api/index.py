from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. 讀取 Google 傳來的 HTML
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            html = data.get('html', '')
            
            # 2. 暴力搜索 BigGo 特徵 (n:品名, p:價格, s:商店)
            items = []
            # BigGo 的資料格式通常是 "n":"...","p":...
            pattern = r'"n":"([^"]+)".*?"p":(\d+),"s":"([^"]+)"'
            matches = re.findall(pattern, html)

            for n, p, s in matches:
                if len(n) > 5: # 過濾掉雜訊
                    items.append({
                        "title": n,
                        "price": int(p),
                        "shop": s
                    })

            # 3. 回傳 JSON 陣列
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析錯誤: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Parser is online. Send POST with HTML.")