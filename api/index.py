from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 接收 Google 傳過來的 HTML 內容
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        html = data.get('html', '')

        items = []
        # 使用 Python 暴力搜索關鍵特徵
        # BigGo 網頁中即使用 JS 渲染，資料通常還是會以 "n":"品名","p":價格 存在
        pattern = r'"n":"([^"]+)".*?"p":(\d+),"s":"([^"]+)"'
        matches = re.findall(pattern, html)

        for n, p, s in matches[:20]:
            items.append({
                "title": n,
                "price": int(p),
                "shop": s
            })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(items).encode('utf-8'))

    def do_GET(self): # 保留 GET 供測試
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"API is running. Please use POST from GAS.")