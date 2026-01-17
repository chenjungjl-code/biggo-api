from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            url = data.get('url', '').replace('biggo.uk', 'biggo.com.tw')
            
            # 強制設定為台灣版請求標頭
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': 'biggo_country=tw; lang=zh-TW', # 關鍵：強制指定台灣
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8',
                'Referer': 'https://biggo.com.tw/'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            # 針對台灣版結構抓取
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                try:
                    name = n.encode().decode('unicode_escape')
                except:
                    name = n.replace('\\', '')
                if len(name) > 5:
                    items.append({"title": name, "price": int(p), "shop": "BigGoTW"})

            # 如果還是失敗，回傳前 300 字看看有沒有被導向
            if not items:
                items.append({"title": f"DEBUG_URL: {url} | CONTENT: {html[:300]}", "price": 0, "shop": "SYSTEM"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:25], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"ERROR: {str(e)}", "price": 0, "shop": "SYSTEM"}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TW-Forced Scraper Ready")