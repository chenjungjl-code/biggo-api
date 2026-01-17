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
            
            # --- 1. 深度清洗還原 ---
            # 有些轉義會變成 \u0022 (") 或 \/ (/)
            html = html.replace('\\u0022', '"').replace('\\/', '/')
            html = html.replace('\\"', '"') # 處理正常的轉義引號
            
            # --- 2. 萬能正則掃描 ---
            # 模式 A: 尋找所有 "n":"..." 和 "p":123 (允許中間有任何空格)
            # 模式 B: 尋找 "name":"..." 和 "price":123
            items = []
            patterns = [
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)',
                r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, html)
                for n, price in matches:
                    # 處理編碼過的品名 (如 \u6d17\u8863)
                    try:
                        clean_n = n.encode().decode('unicode_escape')
                    except:
                        clean_n = n
                    
                    if 5 < len(clean_n) < 150:
                        items.append({
                            "title": clean_n.strip(),
                            "price": int(price),
                            "shop": "BigGo比價"
                        })

            # --- 3. 去重與排序 (取前 20 筆) ---
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_results.append(item)
                    seen.add(item['title'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_results[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析異常: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scan Parser Ready.")