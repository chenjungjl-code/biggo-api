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
            
            items = []
            
            # 策略 A: 針對 BigGo 的特殊屬性 data-n 和 data-p (如果有的話)
            # 或是在腳本標籤內的特定格式
            raw_patterns = [
                r'"n":"([^"]+?)".*?"p":(\d+)',           # 傳統格式
                r'name":"([^"]+?)".*?price":(\d+)',       # 標準格式
                r'title":"([^"]+?)".*?price":(\d+)',      # 變體格式
                r'\"n\":\"([^"]+?)\",\"p\":(\d+)'         # 帶轉義格式
            ]
            
            for pattern in raw_patterns:
                matches = re.findall(pattern, html, re.S)
                for n, p in matches:
                    if len(n) > 8 and len(n) < 100: # 確保品名長度合理
                        items.append({
                            "title": n.encode().decode('unicode_escape', 'ignore') if '\\u' in n else n,
                            "price": int(p),
                            "shop": "BigGo比價"
                        })
            
            # 策略 B: 針對 unicode 編碼處理 (BigGo 常見)
            # 例如 \u6d17\u8863\u7cbe
            if not items:
                unicode_matches = re.findall(r'\\u[0-9a-fA-F]{4}', html)
                if unicode_matches:
                    # 如果發現大量 unicode，嘗試直接抓取價格周圍的文字
                    items.append({"title": "偵測到加密編碼，正在嘗試解析...", "price": 0, "shop": "System"})

            # 去重
            unique_items = []
            seen = set()
            for item in items:
                if item['title'] not in seen and item['price'] > 0:
                    unique_items.append(item)
                    seen.add(item['title'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_items[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner v3 Active")