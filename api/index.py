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
            
            # --- 策略：針對 BigGo 網頁特徵的三種正則模式 ---
            # 模式 1: 帶斜線轉義 \"n\":\"...\",\"p\":123
            # 模式 2: 標準引號 "n":"...", "p":123
            # 模式 3: Unicode 轉義 \u0022n\u0022:\u0022...\u0022
            patterns = [
                r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)',
                r'"n"\s*:\s*"(.+?)"\s*,\s*"p"\s*:\s*(\d+)',
                r'\\u0022n\\u0022\s*:\s*\\u0022(.+?)\\u0022\s*,\s*\\u0022p\\u0022\s*:\s*(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, html)
                for n, price in matches:
                    # 解碼 Unicode (如 \u6d17 轉中文)
                    try:
                        # 處理雙重轉義
                        clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                    except:
                        try:
                            clean_n = n.encode('utf-8').decode('unicode_escape')
                        except:
                            clean_n = n.replace('\\', '')
                    
                    if 5 < len(clean_n) < 150:
                        items.append({
                            "title": clean_n.strip(),
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
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # ensure_ascii=False 徹底解決試算表亂碼
            response = json.dumps(unique_results[:20], ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Brute Force Scanner Ready.")