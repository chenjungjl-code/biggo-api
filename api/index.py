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
            
            # 策略 A: 針對 BigGo 可能的 Unicode 混淆進行解碼
            # 有時候資料會長這樣: \u0022n\u0022:\u0022Ariel\u0022
            decoded_html = html.encode().decode('unicode_escape', 'ignore')
            
            items = []
            # 同時在原始與解碼後的 HTML 中搜尋
            sources = [html, decoded_html]
            
            for source in sources:
                # 嘗試多種匹配模式
                patterns = [
                    r'"n":"([^"]+?)".*?"p":(\d+)',
                    r'name":"([^"]+?)".*?price":(\d+)',
                    r'title":"([^"]+?)".*?price":(\d+)'
                ]
                for p in patterns:
                    for n, price in re.findall(p, source):
                        if 5 < len(n) < 100:
                            items.append({"title": n, "price": int(price), "shop": "BigGo比價"})

            # 如果還是空，抓取 HTML 中的腳本區塊 (Script) 做最後診斷
            if not items:
                scripts = re.findall(r'<script.*?> (.*?)</script>', html, re.S)
                for s in scripts[:5]:
                    if "n" in s and "p" in s: # 如果腳本裡有類似格式
                        items.append({"title": "找到潛在資料塊，請檢查解析規則", "price": 0, "shop": "System"})

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
        self.wfile.write(b"Diagnostic Parser Online")