import requests
import xml.etree.ElementTree as ET
import os
import sys

# 1. 监控源和敏感词配置
TRUMP_TWITTER_RSS = "https://rsshub.app/twitter/user/realDonaldTrump"
KEYWORDS = ["iran", "oil", "crude", "fed", "rate", "powell", "伊朗", "原油", "美联储", "降息", "加息"]

def run_monitor():
    # 2. 从环境变量读取密钥
    bark_key = os.environ.get("MY_BARK_KEY")
    if not bark_key:
        print("错误: 未配置环境变量 MY_BARK_KEY")
        sys.exit(1)

    bark_base_url = f"https://api.day.app/{bark_key}/"

    try:
        # 3. 拉取推特数据
        response = requests.get(TRUMP_TWITTER_RSS, timeout=15)
        if response.status_code != 200:
            print(f"无法连接 RSS，状态码: {response.status_code}")
            return

        root = ET.fromstring(response.content)
        items = root.findall('.//item')

        if not items:
            print("没有发现推特")
            return

        # 4. 只检查最新一条推特
        latest_item = items[0]
        title = latest_item.find('title').text or ""
        link = latest_item.find('link').text or ""
        text_lower = title.lower()

        # 5. 敏感词匹配
        if any(word in text_lower for word in KEYWORDS):
            # 6. 推送提醒
            push_url = f"{bark_base_url}【特朗普突发】/{title}?group=Trump&sound=alarm&url={link}"
            requests.get(push_url, timeout=5)
            print(f"成功推送: {title}")
        else:
            print(f"检查完毕，无敏感内容: {title[:30]}...")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    run_monitor()
