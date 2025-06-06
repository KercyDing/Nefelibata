"""
AI客户端封装
提供线程化的AI聊天功能
"""
import requests
import json
from PyQt6.QtCore import QThread, pyqtSignal
from typing import List, Dict, Any, Optional

from models import AIProviderFactory


class AIChatThread(QThread):
    """AI聊天线程（非流式）"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str, api_key: str, history_messages: Optional[List[Dict]] = None, model: str = "glm-4-flash"):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key
        self.history_messages = history_messages or []
        self.model = model

    def run(self):
        try:
            # 构建完整的消息列表，确保不重复
            if not self.history_messages:
                messages = [{"role": "user", "content": self.prompt}]
            else:
                # 移除最后一个重复的消息
                messages = self.history_messages[:-1] + [{"role": "user", "content": self.prompt}]
            
            # 使用工厂创建AI服务提供商
            provider = AIProviderFactory.create_provider(self.model, self.api_key)
            ai_response = provider.chat(messages=messages, model=self.model)
            
            self.response_received.emit(ai_response)
        except requests.exceptions.RequestException as e:
            error_message = f"网络请求错误: {e}"
            self.error_occurred.emit(error_message)
        except Exception as e:
            error_message = f"发生意外错误: {str(e)}"
            self.error_occurred.emit(error_message)


class AIStreamThread(QThread):
    """AI流式聊天线程"""
    chunk_received = pyqtSignal(str)  # 接收到文本片段
    stream_finished = pyqtSignal(str)  # 流式输出完成，发送完整文本
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str, api_key: str, history_messages: Optional[List[Dict]] = None, model: str = "glm-4-flash"):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key
        self.history_messages = history_messages or []
        self.model = model

    def run(self):
        try:
            # 构建完整的消息列表
            if not self.history_messages:
                messages = [{"role": "user", "content": self.prompt}]
            else:
                messages = self.history_messages[:-1] + [{"role": "user", "content": self.prompt}]
            
            # 使用工厂创建AI服务提供商
            provider = AIProviderFactory.create_provider(self.model, self.api_key)
            response = provider.chat(messages=messages, model=self.model, stream=True)
            
            full_content = ""
            
            if self.model.startswith("glm-"):
                # 处理智谱AI的流式响应
                for chunk in response:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        chunk_text = chunk.choices[0].delta.content
                        full_content += chunk_text
                        self.chunk_received.emit(chunk_text)
            else:
                # 处理SiliconFlow的流式响应
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]  # 去掉 'data: ' 前缀
                            if data_str.strip() == '[DONE]':
                                break
                            try:
                                data = json.loads(data_str)
                                if 'choices' in data and data['choices']:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta and delta['content']:
                                        chunk_text = delta['content']
                                        full_content += chunk_text
                                        self.chunk_received.emit(chunk_text)
                            except json.JSONDecodeError:
                                continue
            
            self.stream_finished.emit(full_content)
            
        except requests.exceptions.RequestException as e:
            error_message = f"网络请求错误: {e}"
            self.error_occurred.emit(error_message)
        except Exception as e:
            error_message = f"发生意外错误: {str(e)}"
            self.error_occurred.emit(error_message)
