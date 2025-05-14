import requests
from bs4 import BeautifulSoup

class DataCollector:
    def __init__(self):
        self.url = "https://github.com/topics/ai-tools"
        self.headers = {
            'User-Agent': 'Mozilla/5.0'
        }

    def collect_all_data(self):
        print("开始数据收集...")
        tools = []
        resp = requests.get(self.url, headers=self.headers)
        print("GitHub响应状态码:", resp.status_code)
        if resp.status_code != 200:
            print("请求失败")
            return tools

        soup = BeautifulSoup(resp.text, "html.parser")
        repo_cards = soup.find_all("article", class_="border rounded color-shadow-small color-bg-subtle my-4")
        for card in repo_cards:
            try:
                h3 = card.find("h3")
                name = h3.get_text(strip=True).replace("\n", "").replace(" ", "")
                url = "https://github.com" + h3.find("a")["href"]
                desc_tag = card.find("p", class_="color-fg-muted mb-0")
                desc = desc_tag.get_text(strip=True) if desc_tag else "无描述"
                tools.append({
                    "name": name,
                    "description": desc,
                    "url": url,
                    "source": "GitHub"
                })
                print("找到工具:", name)
            except Exception as e:
                print("解析出错:", e)
        print(f"总共收集到 {len(tools)} 个工具")
        return tools

if __name__ == "__main__":
    collector = DataCollector()
    tools = collector.collect_all_data()
    print(f"收集到 {len(tools)} 个工具")