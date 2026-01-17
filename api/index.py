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
            
            items = []
            
            # --- 策略 A: 尋找 BigGo 的核心 JSON 資料區塊 ---
            # 直接找 "n":"..." 和 "p":123
            matches = re.findall(r'"n"\s*:\s*"(.+?)"\s*,\s*"p"\s*:\s*(\d+)', html)
            
            for n, p in matches:
                try:
                    # 處理編碼
                    clean_n = n.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                except:
                    clean_n = n.replace('\\', '')
                
                if len(clean_n) > 5:
                    items.append({"title": clean_n.strip(), "price": int(p), "shop": "BigGo"})

            # --- 策略 B: 診斷模式 (如果 A 失敗，吐出網頁關鍵字) ---
            if not items:
                # 抓取網頁標題或開頭，回傳給試算表顯示
                debug_text = html[1000:1200].replace('"', "'")
                items.append({
                    "title": f"診斷訊息: 字數{len(html)} - 片段:{debug_text}", 
                    "price": 0, 
                    "shop": "Debug"
                })

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(items[:20], ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps([{"title": f"解析器噴錯: {str(e)}", "price": 0}]).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Diagnostic System Ready.")