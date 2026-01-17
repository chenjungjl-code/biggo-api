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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': 'biggo_country=tw',
                'Accept-Language': 'zh-TW,zh;q=0.9'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            # --- 終極暴力搜尋：不分格式，只要有名稱跟數字價格就抓 ---
            items = []
            
            # 模式 A: 尋找所有 "n":"品名", "p":123 (無視轉義)
            raw_data = re.findall(r'n["\\]+:\s*["\\]+(.+?)["\\]+\s*,\s*["\\]+p["\\]+:\s*(\d+)', html)
            
            # 模式 B: 尋找所有 "name":"品名", "price":123
            if not raw_data:
                raw_data = re.findall(r'name["\\]+:\s*["\\]+(.+?)["\\]+.*?price["\\]+:\s*(\d+)', html)

            for n, p in raw_data:
                # 簡單清理名稱中的 Unicode 和斜線
                clean_n = n.replace('\\u0022', '').replace('\\', '').strip()
                # 還原編碼 (處理像 \u6d17 這種字)
                try:
                    clean_n = clean_n.encode().decode('unicode_escape')
                except:
                    pass
                
                if 5 < len(clean_n) < 100:
                    items.append({"title": clean_n, "price": int(p), "shop": "BigGo比價"})

            # 如果還是空的，抓取網頁中所有出現 $ 數字的標籤片段作為最後診斷
            if not items:
                items.append({"title": f"解析失敗。樣版片段: {html[html.find('price'):html.find('price')+200]}", "price": 0, "shop": "DEBUG"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"錯誤: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Deep Scan Active")