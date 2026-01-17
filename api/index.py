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
            
            # 1. 徹底解碼：還原所有 Unicode 與轉義
            # 處理像 \u0022 (") 和 \/ (/) 以及 \\"
            html = html.replace('\\u0022', '"').replace('\\/', '/').replace('\\"', '"')
            try:
                html = html.encode('utf-8').decode('unicode_escape', 'ignore')
            except:
                pass

            items = []
            
            # 2. 暴力提取模式：針對 BigGo 網頁結構的特徵
            # 我們找尋: "n":"任意文字","p":數字 
            # 注意：使用 re.DOTALL 跨行搜尋
            raw_matches = re.findall(r'"n"\s*:\s*"([^"]+?)"\s*,\s*"p"\s*:\s*(\d+)', html)
            
            # 如果上面失敗，找備用格式 name / price
            if not raw_matches:
                raw_matches = re.findall(r'"name"\s*:\s*"([^"]+?)"\s*,\s*"price"\s*:\s*(\d+)', html)

            for n, p in raw_matches:
                # 排除太短的（可能是按鈕文字）
                if len(n) > 5:
                    items.append({
                        "title": n.replace('\\', ''), 
                        "price": int(p),
                        "shop": "BigGo搜尋"
                    })

            # 3. 去重並限制 20 筆
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
            
            response = json.dumps(unique_results[:20], ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Ultimate Brute Force Parser Ready.")
        