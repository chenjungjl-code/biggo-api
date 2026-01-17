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
            
            # --- 核心修復：強制解碼與還原字串 ---
            # 1. 處理 JSON 雙重轉義
            html = html.replace('\\"', '"').replace('\\\\', '\\')
            
            # 2. 將 \u6d17 轉回中文 (魯棒處理)
            try:
                html = html.encode().decode('unicode_escape')
            except:
                pass

            items = []
            # --- 3. 寬鬆抓取：尋找所有品名與價格配對 ---
            # 模式 1: "n":"品名","p":價格
            # 模式 2: "name":"品名","price":價格
            patterns = [
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)',
                r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, html)
                for n, price in matches:
                    if len(n) > 5 and len(n) < 150:
                        items.append({
                            "title": n.strip(),
                            "price": int(price),
                            "shop": "BigGo比價"
                        })

            # 去重
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen and item['price'] > 0:
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
            # 回傳錯誤訊息輔助診斷
            self.wfile.write(json.dumps([{"title": f"解析器錯誤: {str(e)}", "price": 0}]).encode('utf-8'))