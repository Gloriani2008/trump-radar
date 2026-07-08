from http.server import BaseHTTPRequestHandler
import json
import requests
import xml.etree.ElementTree as ET
import os

# 特朗普推特的 RSS 监控源
TRUMP_TWITTER_RSS = "https://rsshub.app/twitter/user/realDonaldTrump"
# 敏感词库
KEYWORDS = ["iran", "oil", "crude", "fed", "rate", "powell", "伊朗", "原油", "美联储", "降息", "加息"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. 从系统环境变量读取密钥
        bark_key = os.environ.get("MY_BARK_KEY")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if not bark_key:
            response = {"status": "error", "message": "未配置环境变量 MY_BARK_KEY"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return

        bark_base_url = f"https://api.day.app/{bark_key}/"

        try:
            # 2. 抓取推特
            res = requests.get(TRUMP_TWITTER_RSS, timeout=10)
            if res.status_code != 200:
                response = {"status": "error", "message": "无法连接RSS源"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            root = ET.fromstring(res.content)
            items = root.findall('.//item')
            
            if not items:
                response = {"status": "success", "message": "没有发现新推特"}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            # 3. 检查最新一条
            latest_item = items[0]
            title = latest_item.find('title').text or ""
            link = latest_item.find('link').text or ""
            
            text_lower = title.lower()
            if any(word in text_lower for word in KEYWORDS):
                # 4. 触发 Bark 推送
                push_url = f"{bark_base_url}【特朗普突发提及】/{title}?group=Trump&sound=alarm&url={link}"
                requests.get(push_url, timeout=5)
                response = {"status": "pushed", "content": title}
            else:
                response = {"status": "success", "message": "检查完毕，未包含敏感词"}

        except Exception as e:
            response = {"status": "error", "error_msg": str(e)}

        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
