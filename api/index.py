from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 讀取傳入的 HTML 資料
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            html = data.get('html', '')
            
            # 暴力提取 BigGo 資料特徵
            # 格式: "n":"品名","p":價格,"s":"商店"
            items = []
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
            
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))

    # 為了方便瀏覽器測試，保留 do_GET
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Vercel Parser is Ready. Please send POST request.")