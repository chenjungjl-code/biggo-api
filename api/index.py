from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs, unquote

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        target_url = unquote(query.get('url', [None])[0])

        # 提取關鍵字
        try:
            keyword = target_url.split('/s/')[-1].split('/')[0]
        except:
            keyword = "ariel"
        
        # 偽裝成真實瀏覽器的 Headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://biggo.com.tw/",
            "Origin": "https://biggo.com.tw",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        api_url = f"https://biggo.com.tw/api/v1/search?q={keyword}&v=1"
        
        try:
            # 增加一個 session 來處理可能的 cookie
            session = requests.Session()
            # 增加 timeout 到 20 秒，避免 Vercel 太快放棄
            res = session.get(api_url, headers=headers, timeout=20)
            
            if res.status_code == 200:
                data = res.json()
                results = data.get('results', [])
                items = [{"title": r.get('n'), "price": int(r.get('p')), "shop": r.get('s', '網路商城')} for r in results]
            else:
                items = [{"title": f"HTTP Error {res.status_code}", "price": 0, "shop": "Error"}]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20]).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            error_msg = [{"title": f"連線逾時或錯誤: {str(e)}", "price": 0, "shop": "System"}]
            self.wfile.write(json.dumps(error_msg).encode('utf-8'))