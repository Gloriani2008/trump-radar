import requests
import os

def run_monitor():
    bark_key = os.environ.get("MY_BARK_KEY")
    if not bark_key:
        print("未检测到密钥")
        return

    # 添加 Header，伪装成普通浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    }
    
    rss_url = "https://rsshub.app/bilibili/user/dynamic/208259"
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("RSS 连接成功！")
            # 这里是你后续发送推送的代码
        else:
            print(f"无法连接 RSS，状态码: {response.status_code}")
    except Exception as e:
        print(f"连接出错: {e}")

if __name__ == "__main__":
    run_monitor()
