import os
import logging
from datetime import datetime
from scripts.data_collection import DataCollector

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_log.txt'),
        logging.StreamHandler()
    ]
)

def save_to_markdown(tools, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# AI 工具更新报告 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        # Write summary
        total_stars = sum(tool.get('stars', 0) for tool in tools)
        languages = set(tool.get('language', '未知') for tool in tools)
        f.write(f"## 今日更新概览\n\n")
        f.write(f"- 新增工具数量: {len(tools)} 个\n")
        f.write(f"- 总星标数: {total_stars} ⭐\n")
        f.write(f"- 涉及编程语言: {', '.join(languages)}\n\n")
        
        # Group tools by language
        tools_by_language = {}
        for tool in tools:
            lang = tool.get('language', '未知')
            if lang not in tools_by_language:
                tools_by_language[lang] = []
            tools_by_language[lang].append(tool)
        
        # Write tools by language
        for lang, lang_tools in sorted(tools_by_language.items()):
            f.write(f"## {lang} 相关工具\n\n")
            
            for i, tool in enumerate(lang_tools, 1):
                f.write(f"### {i}. {tool['name']} ⭐{tool.get('stars', 0)}\n\n")
                f.write(f"**简要中文解释**: {tool.get('zh_explain', '')}\n\n")
                f.write(f"**描述**: {tool['description']}\n\n")
                f.write(f"**标签**: {', '.join(tool.get('tags', []))}\n\n")
                f.write(f"**GitHub**: [{tool['url']}]({tool['url']})\n\n")
                f.write("---\n\n")

def main():
    logging.info("开始收集AI工具信息...")
    collector = DataCollector()
    try:
        tools = collector.collect_all_data()
        logging.info(f"从 GitHub 收集到 {len(tools)} 个新工具")
    except Exception as e:
        logging.error(f"收集工具信息时发生错误: {str(e)}", exc_info=True)
        return
    
    if not tools:
        logging.warning("未收集到任何工具信息")
        return
    
    os.makedirs("output", exist_ok=True)
    filename = f"output/ai_tools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    save_to_markdown(tools, filename)
    logging.info(f"所有数据已保存到: {filename}")

if __name__ == "__main__":
    main()