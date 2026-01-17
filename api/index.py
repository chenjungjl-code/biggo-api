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
            target_url = data.get('url', '')

            # 強制導向台灣版 BigGo 避免 IP 誤判
            if "biggo.com.tw" not in target_url and "s/" in target_url:
                target_url = target_url.replace("biggo.uk", "biggo.com.tw")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'zh-TW,zh;q=0.9'
            }
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', 'ignore')

            items = []
            # 針對 BigGo 資料特徵的兩大掃描模式
            patterns = [
                r'\\"n\\"\s*:\s*\\"(.+?)\\"\s*,\s*\\"p\\"\s*:\s*(\d+)',
                r'"n"\s*:\s*"([^"]+)"\s*,\s*"p"\s*:\s*(\d+)'
            ]

            for p in patterns:
                matches = re.findall(p, html)
                for n, price in matches:
                    # 徹底修復亂碼邏輯
                    try:
                        clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                    except:
                        try:
                            clean_n = n.encode('utf-8').decode('unicode_escape')
                        except:
                            clean_n = n.replace('\\', '')
                    
                    if len(clean_n) > 5 and len(clean_n) < 150:
                        items.append({"title": clean_n.strip(), "price": int(price), "shop": "BigGo比價"})

            # 去重
            unique_results = []
            seen = set()
            for item in items:
                if item['title'] not in seen:
                    unique_results.append(item)
                    seen.add(item['title'])

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(unique_results[:25], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Final Scraper Online.")