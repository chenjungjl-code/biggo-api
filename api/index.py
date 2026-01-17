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
            # 策略：直接在原始 HTML 搜尋所有可能的商品名稱與價格
            # 模式 A: "n":"...", "p":123 (這是 BigGo 最核心的資料存法)
            # 使用非貪婪匹配並允許中間有混淆符號
            matches = re.findall(r'"n"\s*:\s*"(.+?)"\s*,\s*"p"\s*:\s*(\d+)', html)
            
            for n, p in matches:
                if len(n) > 5:
                    # 處理亂碼：將 \u6d17 這種編碼轉回中文
                    try:
                        clean_n = n.encode('utf-8').decode('unicode_escape')
                    except:
                        clean_n = n.replace('\\u0022', '"').replace('\\', '')
                        
                    items.append({
                        "title": clean_n.strip(),
                        "price": int(p),
                        "shop": "BigGo比價"
                    })

            # 去重與限額
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
            
            # 重要：ensure_ascii=False 解決亂碼關鍵
            response = json.dumps(unique_results[:20], ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scan Active")