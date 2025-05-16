import os
import logging
from datetime import datetime
from scripts.data_collection import DataCollector
from scripts.project_analyzer import ProjectAnalyzer

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
        f.write(f"# AI 工具分析报告 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
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
                f.write(f"**AI 分析报告**:\n\n{tool.get('analysis', '暂无分析')}\n\n")
                f.write(f"**描述**: {tool['description']}\n\n")
                f.write(f"**标签**: {', '.join(tool.get('tags', []))}\n\n")
                f.write(f"**GitHub**: [{tool['url']}]({tool['url']})\n\n")
                f.write("---\n\n")

def main(test_mode=False, max_test_items=3):
    logging.info("开始收集AI工具信息...")
    collector = DataCollector()
    try:
        tools = collector.collect_all_data()
        
        if test_mode and tools:
            # 在测试模式下，只处理少量项目
            logging.info(f"测试模式: 从 {len(tools)} 个工具中只分析 {min(max_test_items, len(tools))} 个")
            tools = tools[:min(max_test_items, len(tools))]
        
        logging.info(f"从 GitHub 收集到 {len(tools)} 个新工具")
        
        if tools:
            # 初始化项目分析器
            try:
                analyzer = ProjectAnalyzer()
                logging.info("正在验证 API 密钥...")
                
                # 先验证 API 密钥是否有效
                if analyzer.check_api_key_validity():
                    logging.info("API 密钥有效，开始分析项目...")
                    
                    # 分析每个项目
                    for i, tool in enumerate(tools):
                        logging.info(f"正在分析项目 {i+1}/{len(tools)}: {tool['name']}")
                        analysis_result = analyzer.analyze_project(tool)
                        tool['analysis'] = analysis_result['analysis']
                    
                    logging.info("项目分析完成")
                else:
                    logging.error("API 密钥无效，将跳过项目分析")
                    for tool in tools:
                        tool['analysis'] = "由于 API 密钥无效，项目分析被跳过。请确保提供有效的 DeepSeek API 密钥。"
                
            except ValueError as e:
                logging.error(f"API 密钥错误: {str(e)}")
                for tool in tools:
                    tool['analysis'] = f"项目分析失败: {str(e)}。请使用 --api-key 参数提供有效的 DeepSeek API 密钥。"
            except Exception as e:
                logging.error(f"项目分析过程中发生错误: {str(e)}", exc_info=True)
                # 继续执行，即使分析失败也保存收集到的数据
                for tool in tools:
                    if 'analysis' not in tool:
                        tool['analysis'] = f"项目分析失败: {str(e)}"
        
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
    import argparse
    parser = argparse.ArgumentParser(description='GitHub AI 工具收集和分析器')
    parser.add_argument('--api-key', type=str, help='DeepSeek API密钥')
    parser.add_argument('--test', action='store_true', help='测试模式：仅分析少量项目')
    parser.add_argument('--test-count', type=int, default=3, help='测试模式下要分析的项目数量（默认3个）')
    args = parser.parse_args()
    
    if args.api_key:
        os.environ['DEEPSEEK_API_KEY'] = args.api_key
    
    main(test_mode=args.test, max_test_items=args.test_count)