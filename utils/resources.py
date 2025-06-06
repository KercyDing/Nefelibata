"""
资源路径管理工具
"""
import sys
import os


def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的可执行文件
        return os.path.join(sys._MEIPASS, relative_path)
    # 如果是开发环境下运行 Python 脚本
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, relative_path)


def get_config_paths():
    """获取配置文件路径"""
    # 配置文件路径
    ini_folder = resource_path('ini')
    if not os.path.exists(ini_folder):
        os.makedirs(ini_folder)
    
    config_file = os.path.join(ini_folder, 'config.ini')
    model_config_file = os.path.join(ini_folder, 'modelconfig.ini')
    key_file = os.path.join(ini_folder, 'config.key')
    model_key_file = os.path.join(ini_folder, 'modelconfig.key')
    
    return {
        'ini_folder': ini_folder,
        'config_file': config_file,
        'model_config_file': model_config_file,
        'key_file': key_file,
        'model_key_file': model_key_file
    }


def get_icon_path():
    """获取应用图标路径"""
    return resource_path("icon/icon.ico" if sys.platform == "win32" else "icon/icon.icns")
