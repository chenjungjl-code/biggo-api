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
            
            # --- 步驟 1: 嘗試還原所有可能的編碼 ---
            # 處理 BigGo 原始碼中最麻煩的雙重轉義
            html = html.replace('\\"', '"').replace('\\\\u', '\\u')
            
            # --- 步驟 2: 多重正則策略 (Regex) ---
            # 增加 re.S (DOTALL) 確保跨行也能抓
            patterns = [
                r'"n"\s*:\s*"([^"]+?)"\s*,\s*"p"\s*:\s*(\d+)', # 標準格式
                r'name":"([^"]+?)".*?"price":(\d+)',           # 變體格式
                r'\"n\":\"([^"]+?)\",\"p\":(\d+)'               # 轉義格式
            ]
            
            for p in patterns:
                matches = re.findall(p, html, re.S)
                for n, price in matches:
                    # 處理品名中的 Unicode (如 \u6d17)
                    try:
                        clean_n = n.encode().decode('unicode_escape')
                    except:
                        clean_n = n
                    
                    if 5 < len(clean_n) < 100 and int(price) > 0:
                        items.append({
                            "title": clean_n,
                            "price": int(price),
                            "shop": "BigGo搜尋"
                        })

            # --- 步驟 3: 最終去重 ---
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
            # 發生意外時，回傳一個偵錯標籤，讓我們知道 Python 運行到哪
            self.wfile.write(json.dumps([{"title": f"解析異常: {str(e)[:50]}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scraper Ready.")