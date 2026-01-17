from http.server import BaseHTTPRequestHandler
import json
import re
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            target_url = data.get('url', '') # 改為接收網址
            
            # 使用 Vercel 伺服器直接請求網頁
            req = urllib.request.Request(
                target_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            # 針對 BigGo 台灣版的 JSON 結構進行地毯式搜索
            matches = re.findall(r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)', html)
            if not matches:
                matches = re.findall(r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)', html)

            for n, p in matches:
                try:
                    clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                except:
                    try:
                        clean_n = n.encode('utf-8').decode('unicode_escape')
                    except:
                        clean_n = n.replace('\\', '')
                
                if len(clean_n) > 5:
                    items.append({"title": clean_n.strip(), "price": int(p), "shop": "BigGo"})

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析失敗: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Direct Scraper Active")