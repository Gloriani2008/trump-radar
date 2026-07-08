from http.server import BaseHTTPRequestHandler
import json
import requests
import xml.etree.ElementTree as ET
import os

TRUMP_TWITTER_RSS = "https://rsshub.app/twitter/user/realDonaldTrump"
KEYWORDS = ["iran", "oil", "crude", "fed", "rate", "powell", "伊朗", "原油", "美联储", "降息", "加息"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 抓取你在后台配置的真实密码
        bark_key = os.environ.get("MY_BARK_KEY")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        if not bark_key:
            self.wfile.write(json.dumps({"status": "error", "message": "云端未配置 MY_BARK_KEY"}).encode('utf-8'))
            return

        bark_base_url = f"https://api.day.app/{bark_key}/"

        try:
            res = requests.get(TRUMP_TWITTER_RSS, timeout=10)
            if res.status_code != 200:
                self.wfile.write(json.dumps({"status": "error", "message": "无法连接RSS"}).encode('utf-8'))
                return
                
            root = ET.fromstring(res.content)
            items = root.findall('.//item')
            
            if not items:
                self.wfile.write(json.dumps({"status": "success", "message": "无最新推特"}).encode('utf-8'))
                return

            latest_item = items[0]
            title = latest_item.find('title').text or ""
            link = latest_item.find('link').text or ""
            
            text_lower = title.lower()
            if any(word in text_lower for word in KEYWORDS):
                push_url = f"{bark_base_url}【特朗普突发】/{title}?group=Trump&sound=alarm&url={link}"
                requests.get(push_url, timeout=5)
                response = {"status": "pushed", "content": title}
            else:
                response = {"status": "success", "message": "安全，未包含敏感词"}

        except Exception as e:
            response = {"status": "error", "error_msg": str(e)}

        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
