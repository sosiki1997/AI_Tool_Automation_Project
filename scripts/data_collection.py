import os
import logging
import requests
from datetime import datetime
import time
import random
import json
from typing import List, Dict, Set

class DataCollector:
    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.seen_file = 'output/github_seen_urls.json'
        self.seen_urls = self._load_seen_urls()
        self.api_base = "https://api.github.com"

    def _load_seen_urls(self) -> Set[str]:
        if os.path.exists(self.seen_file):
            with open(self.seen_file, 'r', encoding='utf-8') as f:
                try:
                    return set(json.load(f))
                except Exception:
                    return set()
        return set()

    def _save_seen_urls(self):
        os.makedirs(os.path.dirname(self.seen_file), exist_ok=True)
        with open(self.seen_file, 'w', encoding='utf-8') as f:
            # 将 URL 列表按字母顺序排序后保存，方便查看
            json.dump(sorted(list(self.seen_urls)), f, ensure_ascii=False, indent=2)

    def show_processed_repos(self) -> List[str]:
        """显示已处理过的仓库列表"""
        if not self.seen_urls:
            print("还没有处理过任何仓库")
            return []
        
        urls = sorted(list(self.seen_urls))
        print(f"\n已处理的仓库 (共 {len(urls)} 个):")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
        return urls

    def clear_processed_repos(self):
        """清空已处理的仓库列表"""
        self.seen_urls.clear()
        if os.path.exists(self.seen_file):
            os.remove(self.seen_file)
        print("已清空所有处理记录")

    def remove_processed_repo(self, url: str):
        """从已处理列表中移除指定的仓库"""
        if url in self.seen_urls:
            self.seen_urls.remove(url)
            self._save_seen_urls()
            print(f"已从处理记录中移除: {url}")
        else:
            print(f"未找到该仓库: {url}")

    def collect_all_data(self):
        """Collect data from GitHub, only new repos not seen before"""
        tools = self._collect_from_github()
        logging.info(f"从 GitHub 收集到 {len(tools)} 个新工具")
        # 更新已抓取url
        for tool in tools:
            self.seen_urls.add(tool['url'])
        self._save_seen_urls()
        return tools

    def _collect_from_github(self):
        """Collect tools from GitHub using the API"""
        tools = []
        topics = ['ai-tools', 'artificial-intelligence', 'machine-learning', 'deep-learning']
        
        for topic in topics:
            try:
                # 使用 GitHub API 搜索带有特定主题的仓库
                url = f"{self.api_base}/search/repositories"
                params = {
                    'q': f'topic:{topic}',
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 20
                }
                
                # 添加随机延迟
                time.sleep(random.uniform(2, 5))
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'items' not in data:
                    logging.warning(f"主题 {topic} 的响应中没有找到 items 字段")
                    continue
                
                repos = data['items']
                logging.info(f"主题 {topic} 找到 {len(repos)} 个仓库")
                
                for repo in repos:
                    try:
                        url = repo['html_url']
                        if url in self.seen_urls:
                            logging.debug(f"仓库已经处理过: {url}")
                            continue
                        
                        name = repo['full_name'].replace('/', ' / ')
                        description = repo['description'] or "无描述"
                        stars = repo['stargazers_count']
                        language = repo['language'] or "未知"
                        
                        # 获取仓库的主题
                        topics_url = f"{self.api_base}/repos/{repo['full_name']}/topics"
                        topics_response = requests.get(topics_url, headers=self.headers)
                        topics_data = topics_response.json()
                        tag_list = topics_data.get('names', [topic])
                        
                        tools.append({
                            "name": name,
                            "description": description,
                            "url": url,
                            "source": "GitHub",
                            "stars": stars,
                            "language": language,
                            "tags": tag_list,
                            "discovered_date": datetime.now().strftime('%Y-%m-%d')
                        })
                        logging.info(f"找到新工具: {name} (⭐ {stars})")
                        
                        # 添加短暂延迟，避免触发 API 限制
                        time.sleep(random.uniform(0.5, 1))
                        
                    except Exception as e:
                        logging.error(f"处理仓库时出错: {str(e)}", exc_info=True)
                        continue
                
            except Exception as e:
                logging.error(f"从 GitHub 主题 {topic} 收集数据时出错: {str(e)}", exc_info=True)
                continue
        
        # Sort tools by stars
        return sorted(tools, key=lambda x: x['stars'], reverse=True)

if __name__ == "__main__":
    collector = DataCollector()
    
    # 添加命令行参数解析
    import argparse
    parser = argparse.ArgumentParser(description='GitHub AI 工具收集器')
    parser.add_argument('--show', action='store_true', help='显示已处理的仓库列表')
    parser.add_argument('--clear', action='store_true', help='清空已处理的仓库列表')
    parser.add_argument('--remove', type=str, help='从已处理列表中移除指定的仓库 URL')
    args = parser.parse_args()
    
    if args.show:
        collector.show_processed_repos()
    elif args.clear:
        collector.clear_processed_repos()
    elif args.remove:
        collector.remove_processed_repo(args.remove)
    else:
        tools = collector.collect_all_data()
        print(f"收集到 {len(tools)} 个新工具")