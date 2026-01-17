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
            
            # 1. 處理國際版 Next.js 結構的商品數據
            # 國際版通常使用 "name" 和 "price" 或 "title"
            items = []
            
            # 嘗試抓取 JSON 數據區塊
            # 模式 A: 台灣版常用 n/p
            matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)
            # 模式 B: 國際版常用 name/price
            if not matches:
                matches = re.findall(r'"name"\s*:\s*"([^"]+)"\s*,\s*"price"\s*:\s*(\d+)', html)

            for n, p in matches:
                # 解決亂碼：雙重解碼 unicode
                try:
                    clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                except:
                    try:
                        clean_n = n.encode('utf-8').decode('unicode_escape')
                    except:
                        clean_n = n.replace('\\', '')

                if len(clean_n) > 5:
                    items.append({
                        "title": clean_n.strip(),
                        "price": int(p),
                        "shop": "BigGo"
                    })

            # 如果還是空，進入暴力模式
            if not items:
                # 尋找所有像價格的數字
                prices = re.findall(r'price":(\d+)', html)
                names = re.findall(r'name":"([^"]+)"', html)
                for i in range(min(len(names), len(prices))):
                    items.append({"title": names[i], "price": int(prices[i]), "shop": "BigGo(Global)"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = json.dumps(items[:20], ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"International Parser Active")