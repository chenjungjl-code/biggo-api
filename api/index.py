from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            url = data.get('url', '').replace("biggo.uk", "biggo.com.tw")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'zh-TW,zh;q=0.9',
                'Cookie': 'biggo_country=tw'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            
            # --- 針對你回傳的標籤特徵進行抓取 ---
            # 1. 抓取品名：通常在 <img> 的 alt 屬性或特定的 title class
            # 2. 抓取價格：針對你看到的 data-price="true">$數字
            
            # 模式 A：尋找價格 (抓取像 $279 的數字)
            # 我們找：data-price="true">\$?(\d+,?\d*)
            price_matches = re.findall(r'data-price="true">\$?([\d,]+)', html)
            
            # 模式 B：尋找品名 (通常在價格附近的 <img> alt 標籤裡)
            name_matches = re.findall(r'alt="([^"]{10,100})"', html)

            for i in range(min(len(name_matches), len(price_matches))):
                price_str = price_matches[i].replace(',', '')
                items.append({
                    "title": name_matches[i].strip(),
                    "price": int(price_str),
                    "shop": "BigGo比價"
                })

            # 備援：如果上面標籤抓不到，嘗試找原本的 JSON 模式
            if not items:
                raw_json_matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
                for n, p in raw_json_matches:
                    items.append({"title": n.replace('\\', ''), "price": int(p), "shop": "BigGo比價"})

            # 如果徹底失敗，回傳更多片段除錯
            if not items:
                items.append({"title": f"診斷: 找到價格{len(price_matches)}個, 品名{len(name_matches)}個", "price": 0, "shop": "DEBUG"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析器噴錯: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HTML Tag Parser Online")