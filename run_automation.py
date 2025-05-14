import os
import logging
from datetime import datetime
from scripts.data_collection import DataCollector

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_log.txt'),
        logging.StreamHandler()
    ]
)

def save_to_text(tools, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for i, tool in enumerate(tools, 1):
            f.write(f"工具 {i}\n")
            f.write(f"名称: {tool['name']}\n")
            f.write(f"描述: {tool['description']}\n")
            f.write(f"链接: {tool['url']}\n")
            f.write(f"来源: {tool['source']}\n")
            f.write("-" * 30 + "\n")

def main():
    logging.info("开始收集AI工具信息...")
    collector = DataCollector()
    tools = collector.collect_all_data()
    if not tools:
        logging.warning("未收集到任何工具信息")
        return
    
    os.makedirs("output", exist_ok=True)
    filename = f"output/ai_tools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    save_to_text(tools, filename)
    logging.info(f"所有数据已保存到: {filename}")

if __name__ == "__main__":
    main()