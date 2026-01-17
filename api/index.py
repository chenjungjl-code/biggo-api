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
            
            # --- 核心邏輯：先強制將所有的 Unicode 轉義還原 ---
            # 這是為了對付 \u6d17\u8863 這種格式
            try:
                # 某些環境下 unicode_escape 處理雙重轉義會更有效
                decoded_text = html.encode('utf-8').decode('unicode_escape')
            except:
                decoded_text = html

            items = []
            
            # --- 2. 針對 BigGo 最新的混淆標籤進行地毯式搜索 ---
            # 模式 A: "n":"品名","p":價格
            # 模式 B: "n":"品名","p":價格 (不含引號的變體)
            # 模式 C: 搜尋 JSON 內的 "n" 和 "p" 配對
            patterns = [
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)',
                r'\\"n\\"\s*:\s*\\"([^"]+)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)',
                r'name":"([^"]+?)".*?price":(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, decoded_text)
                for n, price in matches:
                    # 再次清理可能殘留的轉義符號
                    clean_n = n.replace('\\"', '"').replace('\\', '')
                    if 5 < len(clean_n) < 150:
                        items.append({
                            "title": clean_n.strip(),
                            "price": int(price),
                            "shop": "BigGo比價"
                        })

            # --- 3. 備援方案：如果在解碼文本中找不到，直接掃描原始文本 ---
            if not items:
                raw_matches = re.findall(r'"n":"([^"]+?)".*?"p":(\d+)', html)
                for n, price in raw_matches:
                    try:
                        clean_n = n.encode().decode('unicode_escape')
                    except:
                        clean_n = n
                    items.append({"title": clean_n, "price": int(price), "shop": "BigGo商城"})

            # 去重
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen and item['price'] > 0:
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
            self.wfile.write(json.dumps([{"title": f"解析錯誤: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Brute Force Parser Active")