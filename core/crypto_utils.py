"""
加密工具类
"""
from cryptography.fernet import Fernet
import os


class CryptoManager:
    """加密管理器"""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.key_file = os.path.join(config_dir, 'config.key')
        self.model_key_file = os.path.join(config_dir, 'modelconfig.key')
        
        # 初始化加密套件
        self.cipher_suite = Fernet(self._get_or_create_key(self.key_file))
        self.model_cipher_suite = Fernet(self._get_or_create_key(self.model_key_file))
    
    def _get_or_create_key(self, key_file: str) -> bytes:
        """获取或创建加密密钥"""
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_model_config(self, data: str) -> str:
        """加密模型配置"""
        return self.model_cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_model_config(self, encrypted_data: str) -> str:
        """解密模型配置"""
        return self.model_cipher_suite.decrypt(encrypted_data.encode()).decode()
