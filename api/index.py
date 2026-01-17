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
            
            # 1. 徹底解碼 Unicode 亂碼
            # 使用 unicode_escape 將 \uXXXX 轉回中文
            try:
                decoded_html = html.encode().decode('unicode_escape')
            except:
                decoded_html = html

            items = []
            # 2. 同時搜尋原始與解碼後的內容
            # BigGo 資料核心： "n":"品名","p":價格,"s":"商店"
            pattern = r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)'
            matches = re.findall(pattern, decoded_html)

            for n, p in matches:
                # 過濾無意義的短字串
                if len(n) > 5:
                    # 再次清理品名中殘留的轉義符號
                    clean_n = n.replace('\\', '').replace('u0022', '"')
                    items.append({
                        "title": clean_n,
                        "price": int(p),
                        "shop": "BigGo搜尋"
                    })

            # 3. 去重
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
        self.wfile.write(b"Deep Cleaning Parser Active")