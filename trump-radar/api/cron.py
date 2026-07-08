from flask import Flask, jsonify
import requests
import xml.etree.ElementTree as ET
import os  # 👈 导入系统库

app = Flask(__name__)

# 🔒 【安全修改】不在这里写死密码，而是从 Vercel 的系统环境变量里读取名为 "MY_BARK_KEY" 的变量
BARK_KEY = os.environ.get("MY_BARK_KEY")
BARK_BASE_URL = f"https://api.day.app/{BARK_KEY}/" if BARK_KEY else None

# 特朗普推特的 RSS 监控源
TRUMP_TWITTER_RSS = "https://rsshub.app/twitter/user/realDonaldTrump"

# 敏感词库
KEYWORDS = ["iran", "oil", "crude", "fed", "rate", "powell", "伊朗", "原油", "美联储", "降息", "加息"]

@app.route('/api/cron', methods=['GET', 'POST'])
def trump_monitor_cron():
    # 安全检查：如果发现没配置密钥，直接报错防御
    if not BARK_BASE_URL:
        return jsonify({"status": "error", "message": "云端未配置 BARK 密钥环境变"}), 500

    try:
        response = requests.get(TRUMP_TWITTER_RSS, timeout=10)
        if response.status_code != 200:
            return jsonify({"status": "error", "message": "无法连接RSS源"}), 500
            
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        if not items:
            return jsonify({"status": "success", "message": "没有发现新推特"}), 200

        latest_item = items[0]
        title = latest_item.find('title').text or ""
        link = latest_item.find('link').text or ""
        
        text_lower = title.lower()
        if any(word in text_lower for word in KEYWORDS):
            push_url = f"{BARK_BASE_URL}【特朗普突发提及】/{title}?group=Trump&sound=alarm&url={link}"
            requests.get(push_url, timeout=5)
            return jsonify({"status": "pushed", "content": title}), 200
            
        return jsonify({"status": "success", "message": "检查完毕，未包含敏感词"}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "error_msg": str(e)}), 500

@app.route('/')
def home():
    return "Trump Radar is running securely on Vercel."
