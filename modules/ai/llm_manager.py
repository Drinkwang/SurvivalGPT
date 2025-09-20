#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大语言模型管理器
支持多种AI模型API的统一管理和调用
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class LLMManager:
    """大语言模型管理器类"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.supported_models = {
            "deepseek": {
                "name": "DeepSeek AI",
                "api_base": "https://api.deepseek.com/v1",
                "model_name": "deepseek-chat",
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "openai": {
                "name": "OpenAI GPT",
                "api_base": "https://api.openai.com/v1",
                "model_name": "gpt-3.5-turbo",
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "claude": {
                "name": "Anthropic Claude",
                "api_base": "https://api.anthropic.com/v1",
                "model_name": "claude-3-sonnet-20240229",
                "max_tokens": 4000,
                "temperature": 0.7
            },
            "local": {
                "name": "本地规则引擎",
                "api_base": "local",
                "model_name": "rule_based",
                "max_tokens": 2000,
                "temperature": 0.0
            }
        }
        
        # 当前使用的模型
        self.current_model = self.config_manager.get("ai.current_model", "local")
        
        # API密钥存储
        self.api_keys = {}
        self._load_api_keys()
    
    def _load_api_keys(self):
        """加载API密钥"""
        try:
            keys_config = self.config_manager.get("ai.api_keys", {})
            self.api_keys = keys_config
        except Exception as e:
            print(f"加载API密钥失败: {e}")
            self.api_keys = {}
    
    def set_api_key(self, model_type: str, api_key: str) -> bool:
        """设置API密钥"""
        try:
            self.api_keys[model_type] = api_key
            
            # 保存到配置文件
            current_keys = self.config_manager.get("ai.api_keys", {})
            current_keys[model_type] = api_key
            self.config_manager.set("ai.api_keys", current_keys)
            self.config_manager.save_config()
            
            return True
        except Exception as e:
            print(f"设置API密钥失败: {e}")
            return False
    
    def get_available_models(self) -> Dict[str, Dict]:
        """获取可用的模型列表"""
        available = {}
        for model_id, model_info in self.supported_models.items():
            # 检查是否有API密钥（本地模型除外）
            if model_id == "local" or model_id in self.api_keys:
                available[model_id] = model_info.copy()
                available[model_id]["has_api_key"] = True
            else:
                available[model_id] = model_info.copy()
                available[model_id]["has_api_key"] = False
        
        return available
    
    def set_current_model(self, model_id: str) -> bool:
        """设置当前使用的模型"""
        if model_id not in self.supported_models:
            return False
        
        # 检查是否有API密钥（本地模型除外）
        if model_id != "local" and model_id not in self.api_keys:
            return False
        
        self.current_model = model_id
        self.config_manager.set("ai.current_model", model_id)
        self.config_manager.save_config()
        
        return True
    
    def get_current_model_info(self) -> Dict:
        """获取当前模型信息"""
        model_info = self.supported_models.get(self.current_model, {})
        model_info["model_id"] = self.current_model
        model_info["has_api_key"] = self.current_model == "local" or self.current_model in self.api_keys
        return model_info
    
    def generate_response(self, prompt: str, context: str = "", scenario: str = "normal") -> Dict:
        """生成AI响应"""
        try:
            if self.current_model == "local":
                return self._generate_local_response(prompt, context, scenario)
            else:
                return self._generate_api_response(prompt, context, scenario)
        except Exception as e:
            return {
                "success": False,
                "response": f"生成响应时发生错误: {str(e)}",
                "model": self.current_model,
                "error": str(e)
            }
    
    def _generate_local_response(self, prompt: str, context: str, scenario: str) -> Dict:
        """使用本地规则引擎生成响应"""
        # 这里可以集成原有的规则引擎逻辑
        from .qa_engine import QAEngine
        
        # 简化的本地响应逻辑
        response = f"基于本地规则引擎的回答：\n\n{prompt}\n\n这是一个{scenario}场景下的生存问题。请查看相关的生存知识和技能指导。"
        
        return {
            "success": True,
            "response": response,
            "model": "local",
            "tokens_used": len(response),
            "scenario": scenario
        }
    
    def _generate_api_response(self, prompt: str, context: str, scenario: str) -> Dict:
        """使用API生成响应"""
        model_info = self.supported_models[self.current_model]
        api_key = self.api_keys.get(self.current_model)
        
        if not api_key:
            return {
                "success": False,
                "response": f"未设置{model_info['name']}的API密钥",
                "model": self.current_model
            }
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(scenario)
        
        # 构建请求数据
        if self.current_model == "deepseek":
            return self._call_deepseek_api(system_prompt, prompt, context, model_info, api_key)
        elif self.current_model == "openai":
            return self._call_openai_api(system_prompt, prompt, context, model_info, api_key)
        elif self.current_model == "claude":
            return self._call_claude_api(system_prompt, prompt, context, model_info, api_key)
        else:
            return {
                "success": False,
                "response": f"不支持的模型类型: {self.current_model}",
                "model": self.current_model
            }
    
    def _build_system_prompt(self, scenario: str) -> str:
        """构建系统提示词"""
        base_prompt = "你是一个专业的生存专家和AI助手，专门为用户提供各种生存场景下的专业建议和指导。"
        
        scenario_prompts = {
            "normal": "当前场景是普通的野外生存环境。请提供实用的生存技巧和建议。",
            "zombie": "当前场景是僵尸末日。需要考虑僵尸威胁、资源稀缺、避难所安全等因素。",
            "biochemical": "当前场景是生化危机。需要考虑生化污染、防护措施、净化处理等因素。",
            "nuclear": "当前场景是核辐射环境。需要考虑辐射防护、安全区域、去污处理等因素。",
            "alien": "当前场景是外星人入侵。需要考虑未知威胁、隐蔽行动、通讯中断等因素。",
            "natural_disaster": "当前场景是自然灾害。需要考虑地震、洪水、火灾等自然威胁。"
        }
        
        scenario_prompt = scenario_prompts.get(scenario, scenario_prompts["normal"])
        
        return f"{base_prompt}\n\n{scenario_prompt}\n\n请用中文回答，提供具体可行的建议，包括步骤说明和注意事项。"
    
    def _call_deepseek_api(self, system_prompt: str, prompt: str, context: str, model_info: Dict, api_key: str) -> Dict:
        """调用DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({"role": "user", "content": f"背景信息：{context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model_info["model_name"],
                "messages": messages,
                "max_tokens": model_info["max_tokens"],
                "temperature": model_info["temperature"],
                "stream": False
            }
            
            response = requests.post(
                f"{model_info['api_base']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "model": self.current_model,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "response": f"API调用失败: {response.status_code} - {response.text}",
                    "model": self.current_model
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"DeepSeek API调用异常: {str(e)}",
                "model": self.current_model,
                "error": str(e)
            }
    
    def _call_openai_api(self, system_prompt: str, prompt: str, context: str, model_info: Dict, api_key: str) -> Dict:
        """调用OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({"role": "user", "content": f"背景信息：{context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "model": model_info["model_name"],
                "messages": messages,
                "max_tokens": model_info["max_tokens"],
                "temperature": model_info["temperature"]
            }
            
            response = requests.post(
                f"{model_info['api_base']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["choices"][0]["message"]["content"],
                    "model": self.current_model,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "response": f"OpenAI API调用失败: {response.status_code} - {response.text}",
                    "model": self.current_model
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"OpenAI API调用异常: {str(e)}",
                "model": self.current_model,
                "error": str(e)
            }
    
    def _call_claude_api(self, system_prompt: str, prompt: str, context: str, model_info: Dict, api_key: str) -> Dict:
        """调用Claude API"""
        try:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Claude API格式稍有不同
            full_prompt = system_prompt
            if context:
                full_prompt += f"\n\n背景信息：{context}"
            full_prompt += f"\n\n用户问题：{prompt}"
            
            data = {
                "model": model_info["model_name"],
                "max_tokens": model_info["max_tokens"],
                "temperature": model_info["temperature"],
                "messages": [
                    {"role": "user", "content": full_prompt}
                ]
            }
            
            response = requests.post(
                f"{model_info['api_base']}/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result["content"][0]["text"],
                    "model": self.current_model,
                    "tokens_used": result.get("usage", {}).get("output_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "response": f"Claude API调用失败: {response.status_code} - {response.text}",
                    "model": self.current_model
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Claude API调用异常: {str(e)}",
                "model": self.current_model,
                "error": str(e)
            }
    
    def test_api_connection(self, model_id: str) -> Dict:
        """测试API连接"""
        if model_id == "local":
            return {
                "success": True,
                "message": "本地规则引擎连接正常",
                "model": model_id
            }
        
        if model_id not in self.api_keys:
            return {
                "success": False,
                "message": f"未设置{model_id}的API密钥",
                "model": model_id
            }
        
        # 发送测试请求
        old_model = self.current_model
        self.current_model = model_id
        
        try:
            result = self.generate_response("测试连接", "", "normal")
            self.current_model = old_model
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"{self.supported_models[model_id]['name']} API连接正常",
                    "model": model_id
                }
            else:
                return {
                    "success": False,
                    "message": f"{self.supported_models[model_id]['name']} API连接失败: {result.get('error', '未知错误')}",
                    "model": model_id
                }
        except Exception as e:
            self.current_model = old_model
            return {
                "success": False,
                "message": f"测试连接时发生异常: {str(e)}",
                "model": model_id
            }
    
    def get_usage_stats(self) -> Dict:
        """获取使用统计"""
        # 这里可以添加使用统计逻辑
        return {
            "current_model": self.current_model,
            "total_requests": 0,
            "total_tokens": 0,
            "models_configured": len([k for k in self.api_keys.keys() if k != "local"]) + 1
        }