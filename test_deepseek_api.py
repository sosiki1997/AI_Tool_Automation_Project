#!/usr/bin/env python3
"""
测试 DeepSeek API 连接
用法: python3 test_deepseek_api.py <your-api-key>
"""

import sys
import requests
import json

def test_deepseek_api(api_key):
    """测试 DeepSeek API 连接"""
    print(f"使用 API 密钥: {api_key[:8]}...")
    
    # 标准 API 端点
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
    # 常用模型名称尝试列表
    models_to_try = [
        "deepseek-chat",
        "deepseek-coder",
        "deepseek-llm",
        "deepseek-v2",
        "deepseek-large"
    ]
    
    # 尝试不同的认证格式
    auth_formats = [
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"Authorization": api_key, "Content-Type": "application/json"},
        {"X-API-Key": api_key, "Content-Type": "application/json"}
    ]
    
    success = False
    
    print("\n开始测试 DeepSeek API 连接...")
    print("=" * 50)
    
    # 1. 首先尝试获取可用模型列表（如果API支持）
    print("\n尝试获取可用模型列表...")
    for auth in auth_formats:
        try:
            models_url = "https://api.deepseek.com/v1/models"  # 假设的模型列表端点
            print(f"使用认证格式: {auth}")
            response = requests.get(models_url, headers=auth, timeout=10)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("成功获取模型列表!")
                try:
                    models = response.json()
                    print(f"可用模型: {json.dumps(models, indent=2, ensure_ascii=False)}")
                    success = True
                    # 如果有可用模型，更新要尝试的模型列表
                    if "data" in models and isinstance(models["data"], list):
                        models_to_try = [model["id"] for model in models["data"]]
                    break
                except:
                    print(f"响应不是有效的 JSON: {response.text[:100]}")
            else:
                print(f"响应: {response.text[:200]}")
        except Exception as e:
            print(f"获取模型列表时出错: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # 2. 测试简单的聊天请求
    print("\n测试简单的聊天请求...")
    for auth in auth_formats:
        for model in models_to_try:
            print(f"\n尝试模型: {model}")
            print(f"使用认证格式: {auth}")
            
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "你好，请简单介绍一下你自己。"}
                    ],
                    "max_tokens": 50
                }
                
                print(f"发送请求到: {api_url}")
                print(f"请求内容: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                
                response = requests.post(
                    api_url, 
                    headers=auth,
                    json=payload,
                    timeout=20
                )
                
                print(f"状态码: {response.status_code}")
                
                try:
                    response_json = response.json()
                    print(f"响应: {json.dumps(response_json, indent=2, ensure_ascii=False)[:500]}...")
                    
                    if response.status_code == 200:
                        print(f"成功! 模型 {model} 工作正常。")
                        success = True
                        print("\n正确的 API 配置是:")
                        print(f"API URL: {api_url}")
                        print(f"模型名称: {model}")
                        print(f"认证头: {auth}")
                        return
                except:
                    print(f"响应不是有效的 JSON: {response.text[:200]}")
            except Exception as e:
                print(f"请求出错: {str(e)}")
    
    if not success:
        print("\n所有尝试均失败。可能的原因:")
        print("1. API 密钥无效或已过期")
        print("2. DeepSeek API 端点或请求格式已更改")
        print("3. 网络连接问题")
        print("4. DeepSeek 服务暂时不可用")
        
        print("\n建议:")
        print("1. 检查您的 API 密钥是否正确")
        print("2. 查看 DeepSeek 的最新 API 文档")
        print("3. 检查网络连接和代理设置")
        print("4. 联系 DeepSeek 客服获取支持")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python3 {sys.argv[0]} <your-api-key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    test_deepseek_api(api_key) 