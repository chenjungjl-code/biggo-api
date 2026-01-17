from http.server import BaseHTTPRequestHandler
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            html = data.get('html', '')
            items = []

            # 策略 A: 搜尋 BigGo 的 JSON 資料區塊 (這是最穩定的)
            # BigGo 通常把商品放在一個巨大的 JSON 陣列裡
            raw_json_matches = re.findall(r'\{"n":"([^"]+)","p":(\d+),"s":"([^"]+)"\}', html)
            
            for n, p, s in raw_json_matches:
                items.append({
                    "title": n,
                    "price": int(p),
                    "shop": s
                })

            # 策略 B: 如果 A 失敗，嘗試抓取另一種常見的屬性格式
            if not items:
                # 搜尋品名: "n":"...", 搜尋價格: "p":...
                names = re.findall(r'"n":"([^"]+)"', html)
                prices = re.findall(r'"p":(\d+)', html)
                # 配對前 20 筆
                for i in range(min(len(names), len(prices), 20)):
                    if len(names[i]) > 5: # 過濾掉太短的字串
                        items.append({
                            "title": names[i],
                            "price": int(prices[i]),
                            "shop": "BigGo商城"
                        })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scanner is ready.")