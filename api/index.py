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
            
            # --- 核心策略：針對 58 萬字的大型網頁進行特徵提取 ---
            # 這是 BigGo 商品資料最穩定的特徵格式
            # 我們改用非貪婪匹配，並允許中間有換行符 (re.S)
            matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html, re.S)
            
            for n, p in matches:
                # 過濾掉一些系統內建的雜項 (通常品名很短)
                if len(n) > 5:
                    items.append({
                        "title": n,
                        "price": int(p),
                        "shop": "BigGo比價"
                    })

            # 如果上面失敗，嘗試另一種 BigGo 可能的格式 (全名+價格)
            if not items:
                matches_alt = re.findall(r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)', html, re.S)
                for n, p in matches_alt:
                    items.append({"title": n, "price": int(p), "shop": "BigGo商城"})

            # 去重與限額
            unique_items = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_items.append(item)
                    seen.add(item['title'])
                if len(unique_items) >= 20: break

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 確保回傳 JSON 格式
            response_json = json.dumps(unique_items)
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # 發生錯誤時回傳空的陣列
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Parser is running.")