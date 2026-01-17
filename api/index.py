from http.server import BaseHTTPRequestHandler
import requests
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs, unquote
        query = parse_qs(urlparse(self.path).query)
        target_url = unquote(query.get('url', [None])[0])

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://biggo.com.tw/"
        }
        
        try:
            res = requests.get(target_url, headers=headers, timeout=15)
            html = res.text
            items = []

            # --- 終極暴力正則：抓取所有 "n":"..." 和 "p":... ---
            # BigGo 的資料即使用 JavaScript 混淆，這兩個 key 通常不會變
            pattern = r'"n":"([^"]+)".*?"p":(\d+)'
            matches = re.findall(pattern, html)

            for n, p in matches:
                # 簡單過濾：品名長度大於 5 且價格大於 10 的才算商品
                if len(n) > 5 and int(p) > 10:
                    items.append({
                        "title": n,
                        "price": int(p),
                        "shop": "BigGo搜尋"
                    })

            # 如果抓到太多重複的，只取前 20 筆
            unique_items = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_items.append(item)
                    seen.add(item['title'])
                if len(unique_items) >= 20: break

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_items).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"Error: {str(e)}", "price": 0}]).encode('utf-8'))