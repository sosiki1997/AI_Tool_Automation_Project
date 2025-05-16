import os
import logging
import requests
import json
import time
from typing import Dict, Any
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ProjectAnalyzer:
    def __init__(self, api_key: str = None):
        self.api_key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'api_keys.json')
        self.api_key = api_key
        
        if not self.api_key:
            # 尝试从配置文件加载
            self.api_key = self._load_api_key()
        
        if not self.api_key:
            # 尝试从环境变量加载
            self.api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not self.api_key:
            # 移除硬编码的API密钥
            raise ValueError("DeepSeek API密钥未设置。请通过--api-key参数或DEEPSEEK_API_KEY环境变量设置API密钥。")
        
        # 保存API密钥以便将来使用
        self._save_api_key(self.api_key)
        
        # 更新为最新的 DeepSeek API 配置
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        # 使用官方 API 端点
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model_name = "deepseek-chat"  # 已验证可用的模型名称
        
        # 创建带有重试机制的会话
        self.session = self._create_retry_session()
    
    def _create_retry_session(self):
        """创建带有重试机制的会话"""
        retry_strategy = Retry(
            total=3,  # 最多重试3次
            backoff_factor=2,  # 指数级增加重试间隔
            status_forcelist=[429, 500, 502, 503, 504],  # 这些状态码触发重试
            allowed_methods=["GET", "POST"]  # 只对GET和POST请求进行重试
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        return session
    
    def _load_api_key(self) -> str:
        """从配置文件加载API密钥"""
        try:
            if not os.path.exists(self.api_key_file):
                return None
            
            with open(self.api_key_file, 'r') as f:
                data = json.load(f)
                
                # 检查密钥是否有效期内
                if 'expires_at' in data and datetime.now() < datetime.fromisoformat(data['expires_at']):
                    return data.get('deepseek_api_key')
            
            return None
        except Exception as e:
            logging.warning(f"加载API密钥时出错: {str(e)}")
            return None
    
    def _save_api_key(self, api_key: str):
        """保存API密钥到配置文件，默认有效期为30天"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.api_key_file), exist_ok=True)
            
            # 保存API密钥和过期时间
            expires_at = datetime.now() + timedelta(days=30)
            data = {
                'deepseek_api_key': api_key,
                'expires_at': expires_at.isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.api_key_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logging.info("API密钥已保存，30天内无需重新输入")
        except Exception as e:
            logging.warning(f"保存API密钥时出错: {str(e)}")
    
    def check_api_key_validity(self) -> bool:
        """检查API密钥是否有效"""
        try:
            # 使用简单的模型列表请求来验证API密钥 - 这比聊天完成请求更轻量级
            logging.debug(f"正在验证 API 密钥: {self.api_key[:8]}...")
            models_url = "https://api.deepseek.com/v1/models"
            response = self.session.get(models_url, headers=self.headers, timeout=15)
            
            # 输出详细的响应信息以便调试
            logging.debug(f"API 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                logging.info("API密钥验证成功")
                # 更新可用模型列表
                try:
                    models = response.json()
                    if "data" in models and isinstance(models["data"], list):
                        model_ids = [model["id"] for model in models["data"]]
                        if model_ids:
                            self.model_name = model_ids[0]  # 使用第一个可用模型
                            logging.info(f"已选择模型: {self.model_name}")
                except Exception as e:
                    logging.warning(f"解析模型列表时出错: {str(e)}")
                
                return True
            else:
                logging.warning(f"API密钥验证失败: {response.status_code}")
                if response.text:
                    logging.warning(f"详细错误: {response.text[:200]}")
                return False
                
        except Exception as e:
            logging.error(f"验证API密钥时出错: {str(e)}")
            return False

    def analyze_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个项目，返回分析结果
        """
        # 构建项目分析提示
        prompt = self._build_analysis_prompt(project_data)
        
        max_retries = 2
        current_retry = 0
        
        while current_retry <= max_retries:
            try:
                logging.debug("发送分析请求到 DeepSeek API")
                
                # 增加超时时间以避免超时错误
                response = self.session.post(
                    self.api_url,
                    headers=self.headers,
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": "你是一个专业的AI项目分析专家，负责分析GitHub上的AI工具项目。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=90  # 增加到90秒以处理复杂分析
                )
                
                # 处理响应
                if response.status_code != 200:
                    logging.error(f"API请求失败: 状态码 {response.status_code}")
                    logging.error(f"响应内容: {response.text}")
                    
                    # 对于可恢复的错误，进行重试
                    if response.status_code in [429, 500, 502, 503, 504]:
                        current_retry += 1
                        retry_wait = 5 * (2 ** current_retry)  # 指数级退避
                        logging.info(f"将在 {retry_wait} 秒后重试 (尝试 {current_retry}/{max_retries})")
                        time.sleep(retry_wait)
                        continue
                    
                    return {
                        "project_name": project_data["name"],
                        "analysis": f"分析失败: API返回错误 {response.status_code}",
                        "analyzed_at": project_data.get("discovered_date", ""),
                        "original_data": project_data
                    }
                
                analysis_result = response.json()
                logging.debug(f"收到API响应: {json.dumps(analysis_result, indent=2)[:200]}...")
                
                # 解析API响应 (根据 DeepSeek API 的实际返回格式调整)
                return {
                    "project_name": project_data["name"],
                    "analysis": analysis_result["choices"][0]["message"]["content"],
                    "analyzed_at": project_data.get("discovered_date", ""),
                    "original_data": project_data
                }
                
            except requests.exceptions.Timeout:
                current_retry += 1
                if current_retry <= max_retries:
                    retry_wait = 5 * (2 ** current_retry)
                    logging.warning(f"请求超时，将在 {retry_wait} 秒后重试 (尝试 {current_retry}/{max_retries})")
                    time.sleep(retry_wait)
                else:
                    logging.error(f"分析项目 {project_data['name']} 时超时，已达到最大重试次数")
                    return {
                        "project_name": project_data["name"],
                        "analysis": "分析失败: 请求超时，请稍后重试或增加超时时间。",
                        "analyzed_at": project_data.get("discovered_date", ""),
                        "original_data": project_data
                    }
            
            except Exception as e:
                logging.error(f"分析项目 {project_data['name']} 时出错: {str(e)}")
                return {
                    "project_name": project_data["name"],
                    "analysis": f"分析失败: {str(e)}",
                    "analyzed_at": project_data.get("discovered_date", ""),
                    "original_data": project_data
                }
        
        # 如果所有重试都失败了
        return {
            "project_name": project_data["name"],
            "analysis": "分析失败: 多次尝试后仍然失败，请检查网络连接或API配置。",
            "analyzed_at": project_data.get("discovered_date", ""),
            "original_data": project_data
        }

    def _build_analysis_prompt(self, project_data: Dict[str, Any]) -> str:
        """
        构建用于项目分析的提示
        """
        return f"""请分析以下AI工具项目并提供专业见解：

项目名称：{project_data['name']}
项目描述：{project_data['description']}
编程语言：{project_data['language']}
Star数量：{project_data['stars']}
标签：{', '.join(project_data['tags'])}

请从以下几个方面进行分析：
1. 项目的主要功能和应用场景
2. 技术特点和创新点
3. 项目的潜在价值和市场前景
4. 代码质量和维护状况评估
5. 建议和改进空间

请用中文回答，并保持专业、客观的分析态度。
""" 