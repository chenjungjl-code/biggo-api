from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request
from urllib.parse import urljoin

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            base_url = data.get('url', '').replace("biggo.uk", "biggo.com.tw")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'zh-TW,zh;q=0.9',
                'Cookie': 'biggo_country=tw'
            }
            
            req = urllib.request.Request(base_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            
            # --- 強化版抓取：同時尋找品名、價格、與連結 ---
            # BigGo 的結構通常是一個 <a> 標籤包住圖片(alt)與價格(data-price)
            # 我們改用更精密的區塊匹配
            blocks = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>.*?alt="([^"]{10,100})".*?data-price="true">\$?([\d,]+)', html, re.S)

            for link, name, price in blocks:
                # 補全相對路徑網址
                full_link = urljoin("https://biggo.com.tw", link)
                clean_price = price.replace(',', '')
                
                items.append({
                    "title": name.strip(),
                    "price": int(clean_price),
                    "link": full_link,
                    "shop": "BigGo"
                })

            # 備援：如果區塊匹配失敗，使用之前的 JSON 模式但嘗試補上連結
            if not items:
                matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
                for n, p in matches:
                    items.append({
                        "title": n.replace('\\', ''),
                        "price": int(p),
                        "link": base_url, # 備援回總頁
                        "shop": "BigGo"
                    })

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Link Scraper Active")