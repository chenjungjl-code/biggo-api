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

            # --- 策略 A: 搜尋完整 JSON 物件 (最穩定) ---
            # 匹配 {"n":"品名","p":價格,"s":"商店"} 這種格式
            matches_a = re.findall(r'\{"n":"([^"]+?)","p":(\d+?),"s":"([^"]+?)"\}', html)
            for n, p, s in matches_a:
                items.append({"title": n, "price": int(p), "shop": s})

            # --- 策略 B: 如果 A 沒抓到，嘗試鬆散匹配 ---
            if not items:
                # 匹配 "n":"品名" ... "p":價格
                # 使用 [^}]*? 確保在同一個物件大括號內
                matches_b = re.findall(r'"n":"([^"]+?)"[^}]*?"p":(\d+)', html)
                for n, p in matches_b:
                    items.append({"title": n, "price": int(p), "shop": "BigGo商城"})

            # --- 策略 C: 針對 window.__INITIAL_STATE__ 進行區塊提取 ---
            if not items:
                # 找到所有 "name":"..." 和 "price":... 的配對
                names = re.findall(r'"name":"([^"]+?)"', html)
                prices = re.findall(r'"price":(\d+)', html)
                for i in range(min(len(names), len(prices), 20)):
                    if len(names[i]) > 5:
                        items.append({"title": names[i], "price": int(prices[i]), "shop": "比價結果"})

            # 移除重複的品名，保留前 15 筆
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
            self.wfile.write(json.dumps([{"title": f"解析發生錯誤: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Power Parser Ready.")