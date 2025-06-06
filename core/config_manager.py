"""
配置管理器
"""
import configparser
import re
from typing import Optional, Dict, Any
from .crypto_utils import CryptoManager


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_paths: Dict[str, str]):
        self.config_paths = config_paths
        self.crypto_manager = CryptoManager(config_paths['ini_folder'])
        
        # 初始化配置
        self.config = configparser.ConfigParser()
        self.model_config = configparser.ConfigParser()
        
        # 读取配置文件
        self.config.read(config_paths['config_file'])
        self.model_config.read(config_paths['model_config_file'])
    
    def get_api_key(self, provider: str) -> str:
        """获取指定提供商的API密钥"""
        try:
            if 'API' not in self.config:
                return ""
            
            key_name = f'{provider}_key'
            if key_name not in self.config['API'] or not self.config['API'][key_name]:
                return ""
            
            encrypted_key = self.config['API'][key_name]
            return self.crypto_manager.decrypt(encrypted_key)
        except Exception as e:
            print(f"获取{provider} API Key失败: {e}")
            return ""
    
    def save_api_key(self, provider: str, key: str):
        """保存API密钥"""
        if 'API' not in self.config:
            self.config.add_section('API')
        
        key_name = f'{provider}_key'
        if key.strip():
            encrypted_key = self.crypto_manager.encrypt(key)
            self.config['API'][key_name] = encrypted_key
        else:
            # 清空密钥
            self.config['API'][key_name] = ""
        
        self._save_config()
    
    def get_current_model(self) -> Optional[str]:
        """获取当前选择的模型"""
        try:
            if (self.model_config.has_section('MODEL_CONFIG') and 
                'model' in self.model_config['MODEL_CONFIG']):
                encrypted_model = self.model_config['MODEL_CONFIG']['model']
                return self.crypto_manager.decrypt_model_config(encrypted_model)
            return None
        except Exception as e:
            print(f"获取模型配置失败: {e}")
            return None
    
    def save_current_model(self, model: str):
        """保存当前选择的模型"""
        if not self.model_config.has_section('MODEL_CONFIG'):
            self.model_config.add_section('MODEL_CONFIG')
        
        encrypted_model = self.crypto_manager.encrypt_model_config(model)
        self.model_config['MODEL_CONFIG']['model'] = encrypted_model
        self._save_model_config()

    def get_api_key_for_model(self, model: str) -> str:
        """根据模型获取对应的API密钥"""
        if model.startswith("deepseek-ai") or model.startswith("Qwen/"):
            # SiliconFlow 提供商支持的模型
            return self.get_api_key("deepseek")
        else:
            # 智谱AI 提供商支持的模型
            return self.get_api_key("glm")
    def validate_api_key(self, api_key: str, model_type: str) -> bool:
        """验证API密钥格式"""
        if not api_key:  # 允许清空API密钥
            return True
            
        if model_type == "glm-4":
            # GLM API密钥格式验证
            return bool(re.match(r'^[a-zA-Z0-9]{32}\.[a-zA-Z0-9]{16}$', api_key))
        elif model_type == "deepseek-ai":
            # SiliconFlow API密钥格式验证（通常以sk-开头）
            return bool(re.match(r'^sk-[a-zA-Z0-9]{48}$', api_key))
        return False
    
    def _save_config(self):
        """保存主配置文件"""
        with open(self.config_paths['config_file'], 'w') as f:
            self.config.write(f)
    
    def _save_model_config(self):
        """保存模型配置文件"""
        with open(self.config_paths['model_config_file'], 'w') as f:
            self.model_config.write(f)
