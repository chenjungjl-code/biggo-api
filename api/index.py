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
            # 策略：直接搜尋 "n":"..." 和 "p":123
            # 注意：BigGo 原始碼中的引號可能帶有斜線 \"n\"
            pattern = r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)'
            matches = re.findall(pattern, html)
            
            # 如果上面抓不到，試試不帶斜線的 (針對不同壓縮格式)
            if not matches:
                pattern_alt = r'"n"\s*:\s*"(.+?)"\s*,\s*"p"\s*:\s*(\d+)'
                matches = re.findall(pattern_alt, html)

            for n, p in matches:
                if len(n) > 5:
                    # 處理亂碼：將 \u6d17 轉回中文
                    try:
                        # 處理雙重轉義的 unicode
                        clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                    except:
                        try:
                            clean_n = n.encode('utf-8').decode('unicode_escape')
                        except:
                            clean_n = n.replace('\\', '')

                    items.append({
                        "title": clean_n.strip(),
                        "price": int(p),
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
            
            # ensure_ascii=False 解決亂碼關鍵
            response = json.dumps(unique_results[:20], ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scan Parser Active")