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
            
            # 第一層解碼：處理 Unicode 轉義
            try:
                # 解決 \u6d17\u8863 這種亂碼
                html = html.encode().decode('unicode_escape')
            except:
                pass

            items = []
            
            # 策略：寬鬆匹配所有包含 "n" 和 "p" 的結構
            # 這裡使用 [\s\S]*? 來跨越任何換行或空格
            # 格式 1: "n":"品名","p":價格
            pattern1 = r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)'
            matches1 = re.findall(pattern1, html)
            
            # 格式 2: "name":"品名","price":價格
            pattern2 = r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)'
            matches2 = re.findall(pattern2, html)

            all_matches = matches1 + matches2

            for n, p in all_matches:
                # 清除可能殘留的轉義字元
                clean_n = n.replace('\\"', '"').replace('\\/', '/')
                if len(clean_n) > 5:
                    items.append({
                        "title": clean_n,
                        "price": int(p),
                        "shop": "BigGo搜尋"
                    })

            # 去重
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
        self.wfile.write(b"Ultra Parser Active")