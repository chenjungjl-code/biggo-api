from http.server import BaseHTTPRequestHandler
import requests
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        target_url = query.get('url', [None])[0]

        if not target_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing URL parameter")
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "zh-TW,zh;q=0.9"
        }
        
        try:
            res = requests.get(target_url, headers=headers, timeout=15)
            html = res.text
            
            # 策略 A: 抓取 window.__INITIAL_STATE__ (這是最完整的資料源)
            items = []
            # 改用更寬鬆的正則，確保能抓到 JSON 塊
            json_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    # 嘗試從多個可能的路徑提取結果
                    results = data.get('search', {}).get('results', [])
                    for r in results:
                        if 'n' in r and 'p' in r:
                            items.append({
                                "title": r['n'],
                                "price": int(r['p']),
                                "shop": r.get('s', '網路商城')
                            })
                except:
                    pass

            # 策略 B: 如果 A 失敗，直接暴力掃描 HTML 裡的商品特徵
            if not items:
                matches = re.findall(r'"n":"([^"]+)","p":(\d+),"s":"([^"]+)"', html)
                for m in matches[:20]:
                    items.append({"title": m[0], "price": int(m[1]), "shop": m[2]})

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # 確保即便沒抓到，也要回傳空陣列 [] 而不是空字串
            self.wfile.write(json.dumps(items).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200) # 即使錯誤也回傳 200 以避免 GAS 崩潰
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))