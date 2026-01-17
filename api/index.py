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
            
            # --- 超級偽裝標頭 ---
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9',
                'Cookie': 'biggo_country=tw; currency=TWD',
                'Referer': 'https://www.google.com/', # 偽裝來源
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            # 模式 1: 抓取 BigGo 台灣版特有的 JSON (n 為品名, p 為價格)
            # 模式 2: 抓取 HTML 內的價格數字標籤 (備援)
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            
            if not matches:
                # 暴力搜尋：尋找所有 "name":"..." 旁邊有 "price":... 的結構
                matches = re.findall(r'"name":"([^"]+?)".*?"price":(\d+)', html)

            for n, p in matches:
                try:
                    name = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                except:
                    name = n.replace('\\', '')
                
                if len(name) > 5:
                    items.append({"title": name.strip(), "price": int(p), "shop": "BigGo比價"})

            # 如果還是失敗，噴出診斷片段（確保這次一定有文字回傳）
            if not items:
                items.append({"title": f"診斷報告: 抓到 {len(html)} 字 | 開頭: {html[:100]}", "price": 0, "shop": "SYSTEM"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"致命錯誤: {str(e)}", "price": 0, "shop": "SYSTEM"}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Super Scraper Online")