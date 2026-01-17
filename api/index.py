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
            
            # 1. 暴力掃描多種可能的 Key
            items = []
            # 格式 A: "n":"品名","p":123
            matches = re.findall(r'"n":"([^"]+)".*?"p":(\d+)', html)
            # 格式 B: title="品名" ... price="123"
            if not matches:
                matches = re.findall(r'title":"([^"]+)".*?price":(\d+)', html)

            for n, p in matches:
                items.append({"title": n, "price": int(p), "shop": "BigGo"})

            # 2. 如果還是沒資料，回傳偵錯訊息
            if not items:
                debug_info = html[:200].replace('"', "'") # 抓前200字
                items = [{"title": f"偵錯: 抓取長度{len(html)} - 內容:{debug_info}", "price": 0, "shop": "Debug"}]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:15]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": "系統錯誤", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Parser Active")