from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(content_length))
            
            # --- 關鍵修正：強制將網域修正為台灣版 ---
            raw_url = data.get('url', '')
            target_url = raw_url.replace("biggo.uk", "biggo.com.tw")
            if "biggo.com.tw" not in target_url:
                target_url = target_url.replace("biggo.com", "biggo.com.tw")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Cookie': 'biggo_country=tw; lang=zh-TW; currency=TWD', # 強制台灣、中文、台幣
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive'
            }
            
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            # 同時搜尋兩種可能的資料標籤 (台灣版 BigGo 常用 n/p)
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                try:
                    # 處理 Unicode 轉義 (如 \u6d17 -> 洗)
                    name = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                except:
                    try:
                        name = n.encode('utf-8').decode('unicode_escape')
                    except:
                        name = n.replace('\\', '')
                
                if len(name) > 5:
                    items.append({"title": name.strip(), "price": int(p), "shop": "BigGoTW"})

            # 如果抓不到商品，把偵測到的網域和 HTML 開頭回傳以便除錯
            if not items:
                debug_msg = f"URL_USED: {target_url} | HTML: {html[:200]}"
                items.append({"title": f"DEBUG_FAIL: {debug_msg}", "price": 0, "shop": "SYSTEM"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(items[:25], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"ERROR: {str(e)}", "price": 0, "shop": "SYSTEM"}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Forced-TW Scraper Online")