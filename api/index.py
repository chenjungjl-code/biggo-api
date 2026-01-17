from http.server import BaseHTTPRequestHandler
import requests
import json
from urllib.parse import urlparse, parse_qs, unquote

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        target_url = unquote(query.get('url', [None])[0])

        # 1. 從 URL 中提取關鍵字 (例如 ariel%20補充包)
        # 假設網址格式為 https://biggo.com.tw/s/keyword/
        keyword = target_url.split('/s/')[-1].split('/')[0]
        
        # 2. 直接請求 BigGo 的數據介面 (這通常是 JSON，不需要解析 HTML)
        # 我們模擬一個帶有推薦參數的請求，這更容易成功
        api_url = f"https://biggo.com.tw/api/v1/search?q={keyword}&v=1"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://biggo.com.tw/",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            res = requests.get(api_url, headers=headers, timeout=10)
            data = res.json() # 直接轉 JSON
            
            items = []
            # 根據 BigGo API 的結構提取資料 (results 下的清單)
            results = data.get('results', [])
            
            for r in results:
                items.append({
                    "title": r.get('n'),      # Name
                    "price": int(r.get('p')), # Price
                    "shop": r.get('s', '網路商城') # Shop
                })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20]).encode('utf-8'))
            
        except Exception as e:
            # 如果 API 請求失敗，回傳一個帶有錯誤訊息的 JSON 供偵錯
            self.send_response(200)
            self.end_headers()
            error_data = [{"title": f"API Error: {str(e)}", "price": 0, "shop": "System"}]
            self.wfile.write(json.dumps(error_data).encode('utf-8'))