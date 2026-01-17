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
            
            # 1. 徹底解碼 Unicode (處理 \u6d17\u8863...)
            try:
                html = html.encode().decode('unicode_escape', 'ignore')
            except:
                pass

            items = []
            
            # 2. 策略：搜尋所有可能的資料塊
            # 模式 A (核心資料): "n":"品名","p":價格
            # 模式 B (混淆格式): "n" : "品名" , "p" : 價格
            # 模式 C (屬性格式): name="品名" price="價格"
            patterns = [
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)',
                r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)',
                r'title\s*=\s*"([^"]+)"\s*price\s*=\s*"(\d+)"'
            ]
            
            for p in patterns:
                matches = re.findall(p, html, re.I)
                for n, price in matches:
                    if len(n) > 5 and len(n) < 100:
                        items.append({
                            "title": n.replace('\\"', '"').strip(),
                            "price": int(price),
                            "shop": "BigGo搜尋"
                        })

            # 3. 終極保險：如果還是沒抓到，嘗試抓取 JSON 陣列裡的標籤
            if not items:
                # 尋找所有類似商品名稱與價格的連續出現
                names = re.findall(r'"n":"([^"]+)"', html)
                prices = re.findall(r'"p":(\d+)', html)
                for i in range(min(len(names), len(prices), 20)):
                    if len(names[i]) > 5:
                        items.append({"title": names[i], "price": int(prices[i]), "shop": "比價結果"})

            # 去重
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen and item['price'] > 1:
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
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Final Scraper Ready.")