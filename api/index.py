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
            
            # 強制使用 utf-8 解碼，避免亂碼
            if isinstance(html, bytes):
                html = html.decode('utf-8', 'ignore')

            # 處理 BigGo 常見的 Unicode 轉義 (如 \u6d17\u8863)
            try:
                html = html.encode('utf-8').decode('unicode_escape')
            except:
                pass

            items = []
            # 寬鬆匹配模式
            patterns = [
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)',
                r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, html)
                for n, price in matches:
                    if len(n) > 2:
                        items.append({
                            "title": n.strip(),
                            "price": int(price),
                            "shop": "BigGo比價"
                        })

            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_results.append(item)
                    seen.add(item['title'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_results[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))