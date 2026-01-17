from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            html = data.get('html', '')
            items = []

            # 策略 1: 找 BigGo 標準 JSON 格式 ("n":"品名","p":123)
            matches = re.findall(r'"n":"([^"]+)".*?"p":(\d+)', html)
            
            # 策略 2: 如果策略 1 沒抓到，改找網頁常見的品名與價格組合 (暴力匹配)
            if len(matches) < 3:
                # 尋找像是 "Ariel... $199" 這種結構的變體
                matches = re.findall(r'title":"([^"]+)".*?price":(\d+)', html)

            for n, p in matches:
                if len(n) > 5:
                    items.append({
                        "title": n,
                        "price": int(p),
                        "shop": "BigGo商城"
                    })

            # 移除重複項
            unique_items = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_items.append(item)
                    seen.add(item['title'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_items[:15]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Parser is running.")