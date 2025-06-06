"""
AI服务提供商客户端
整合了不同AI服务提供商的API接口
"""
import zhipuai
import requests
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """AI服务提供商抽象基类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], model: str, stream: bool = False) -> str:
        """发送聊天请求"""
        pass


class ZhipuAIProvider(AIProvider):
    """智谱AI服务提供商"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = zhipuai.ZhipuAI(api_key=api_key)    
        
    def chat(self, messages: List[Dict[str, str]], model: str = "glm-z1-flash", stream: bool = False) -> str:
        """发送GLM聊天请求"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream
            )
            
            if not response.choices:
                raise KeyError("API响应中未找到有效回复内容")
            
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"GLM API请求错误: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\n响应状态码: {e.response.status_code}"
                try:
                    error_detail = e.response.json()
                    error_msg += f"\n错误详情: {error_detail}"
                except:
                    error_msg += f"\n响应内容: {e.response.text}"
            raise Exception(error_msg)


class SiliconFlowProvider(AIProvider):
    """硅基流动AI服务提供商（支持DeepSeek、Qwen等模型）"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }    
    def chat(self, messages: List[Dict[str, str]], model: str = "deepseek-ai/DeepSeek-V3", stream: bool = False) -> str:
        """发送SiliconFlow聊天请求"""
        try:
            # 根据模型添加适当的系统消息
            if model.startswith("deepseek-ai"):
                system_message = {"role": "system", "content": "你是由中国的深度求索公司开发的智能助手DeepSeek。"}
            elif model.startswith("Qwen/"):
                system_message = {"role": "system", "content": "你是阿里云开发的通义千问大模型，一个有用、无害、诚实的AI助手。"}
            else:
                # 对于其他模型，不添加特定的身份声明
                system_message = {"role": "system", "content": "你是一个有用、无害、诚实的AI助手。"}
            
            full_messages = [system_message] + messages
            
            payload = {
                "model": model,
                "stream": stream,
                "messages": full_messages
            }
            
            response = requests.post(self.url, json=payload, headers=self.headers)
            
            if response.status_code == 403:
                error_msg = "API认证失败(403 Forbidden)。可能的原因：\n"
                error_msg += "1. API密钥无效或已过期\n"
                error_msg += "2. API密钥没有访问该模型的权限\n"
                error_msg += "3. 账户余额不足或已被禁用"
                raise Exception(error_msg)
            
            response.raise_for_status()
            response_json = response.json()
            
            if "choices" not in response_json or not response_json["choices"]:
                raise KeyError("API响应中未找到有效的回复内容")
            
            return response_json["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            error_msg = ""
            if isinstance(e, requests.exceptions.Timeout):
                error_msg = "API请求超时，请稍后重试。可能的原因：\n"
                error_msg += "1. 服务器响应时间过长\n"
                error_msg += "2. 网络连接不稳定\n" 
                error_msg += "3. 服务器负载过高"
            else:
                error_msg = f"SiliconFlow API请求错误: {str(e)}\n"
                
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"响应状态码: {e.response.status_code}\n"
                try:
                    error_detail = e.response.json()
                    error_msg += f"错误详情: {error_detail}"
                except:
                    error_msg += f"响应内容: {e.response.text}"
            raise Exception(error_msg)
            
        except (KeyError, IndexError) as e:
            raise Exception(f"API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"SiliconFlow错误: {str(e)}")


class AIProviderFactory:
    """AI服务提供商工厂"""      
    @staticmethod
    def create_provider(model: str, api_key: str) -> AIProvider:
        """根据模型名称创建相应的服务提供商"""
        if model.startswith("deepseek-ai") or model.startswith("Qwen/"):
            return SiliconFlowProvider(api_key)
        else:
            return ZhipuAIProvider(api_key)
    
    @staticmethod
    def get_supported_models() -> Dict[str, List[str]]:
        """获取支持的模型列表"""
        return {
            "智谱AI": [
                "glm-z1-flash",
                "glm-z1-airx",
                "glm-z1-air",
                "glm-4-plus"
            ],
            "SiliconFlow": [
                "deepseek-ai/DeepSeek-V3",
                "deepseek-ai/DeepSeek-R1",
                "Qwen/Qwen3-235B-A22B"
            ]
        }


# 为了兼容性，保留原有的类名
ZhipuAI = ZhipuAIProvider
SiliconFlowAI = SiliconFlowProvider
