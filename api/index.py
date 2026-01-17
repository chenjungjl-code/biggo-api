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

            # --- 核心邏輯：鎖定 INITIAL_STATE 區塊 ---
            # 這是 BigGo 目前最核心的資料存放區
            state_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            
            if state_match:
                try:
                    state_json = json.loads(state_match.group(1))
                    # 嘗試從 search results 結構中提取
                    raw_results = state_json.get('search', {}).get('results', [])
                    for r in raw_results:
                        if 'n' in r and 'p' in r:
                            items.append({
                                "title": r['n'],
                                "price": int(r['p']),
                                "shop": r.get('s', '網路商城')
                            })
                except:
                    pass

            # --- 備用方案：暴力正則 (如果 INITIAL_STATE 結構改變) ---
            if not items:
                # 匹配 "n":"品名" 和 "p":價格
                matches = re.findall(r'"n":"([^"]+?)".*?"p":(\d+)', html)
                for n, p in matches:
                    if len(n) > 5:
                        items.append({"title": n, "price": int(p), "shop": "BigGo商城"})

            # 移除重複，取前 15 筆
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_results.append(item)
                    seen.add(item['title'])
                if len(unique_results) >= 15: break

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_results).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析失敗: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Parser Ready.")