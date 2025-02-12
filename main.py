import sys
import traceback
import requests
import uuid
import sqlite3
import re
from PyQt6.QtWidgets import (QApplication, QWidget, QTextEdit, QLineEdit,
                             QVBoxLayout, QMessageBox, QPushButton,
                             QHBoxLayout, QLabel, QDialog, QFormLayout,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QPropertyAnimation, QSize, QPoint, QTimer, QEasingCurve
from PyQt6.QtGui import QFont, QTextCursor, QColor, QIcon, QPixmap
from PyQt6 import QtGui
from cryptography.fernet import Fernet
import configparser
import os
from chat_db import ChatDatabase
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter
import math

# 启用高DPI缩放支持
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

# 获取资源文件的绝对路径
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # 如果是打包后的可执行文件
        return os.path.join(sys._MEIPASS, relative_path)
    # 如果是开发环境下运行 Python 脚本
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

# 设置窗口图标
icon_path = resource_path("icon/icon.ico")

# 配置文件路径
ini_folder = resource_path('ini')
if not os.path.exists(ini_folder):
    os.makedirs(ini_folder)
config_file = os.path.join(ini_folder, 'config.ini')
model_config_file = os.path.join(ini_folder, 'modelconfig.ini')

# 密钥文件路径
key_file = os.path.join(ini_folder, 'config.key')
model_key_file = os.path.join(ini_folder, 'modelconfig.key')

# 检查密钥文件是否存在
if os.path.exists(key_file):
    # 读取密钥
    with open(key_file, 'rb') as f:
        key = f.read()
else:
    # 生成新密钥并保存
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)

# 检查模型配置密钥文件是否存在
if os.path.exists(model_key_file):
    # 读取密钥
    with open(model_key_file, 'rb') as f:
        model_key = f.read()
else:
    # 生成新密钥并保存
    model_key = Fernet.generate_key()
    with open(model_key_file, 'wb') as f:
        f.write(model_key)

cipher_suite = Fernet(key)
model_cipher_suite = Fernet(model_key)

# 读取配置文件
config = configparser.ConfigParser()
config.read(config_file)

# 读取模型配置文件
model_config = configparser.ConfigParser()
model_config.read(model_config_file)


class AIChatThread(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt, api_key, history_messages=None, model="glm-4-flash"):
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
            
            # 根据模型选择不同的API调用方式
            if self.model.startswith("deepseek-ai") or self.model.startswith("Pro/deepseek-ai"):
                from siliconflow import DeepSeekAI
                client = DeepSeekAI(api_key=self.api_key)
                ai_response = client.chat(messages=messages, model=self.model)
            else:
                from glm import ZhipuAI
                client = ZhipuAI(api_key=self.api_key)
                ai_response = client.chat(messages=messages, model=self.model)
            
            self.response_received.emit(ai_response)
        except requests.exceptions.RequestException as e:
            error_message = f"网络请求错误: {e}"
            self.error_occurred.emit(error_message)
            print(error_message)
        except Exception as e:
            error_message = f"发生意外错误: {str(e)}"
            self.error_occurred.emit(error_message)
            print(error_message)


class ModelSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择模型")
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 创建模型选项
        models = [
            ("glm-4-flash", "免费"),
            ("glm-4-flashx", "高速低价"),
            ("glm-4-air", "性价比高"),
            ("glm-4-plus", "旗舰"),
            ("deepseek-ai/DeepSeek-V3", "快速精准"),
            ("Pro/deepseek-ai/DeepSeek-R1", "稳定，需硅基流动官网充值"),
            ("deepseek-ai/DeepSeek-R1", "最强推理大模型"),
            ("Pro/deepseek-ai/DeepSeek-R1", "稳定，需硅基流动官网充值")
        ]

        self.model_buttons = []
        
        # 获取API密钥状态
        glm_key = ""
        deepseek_key = ""
        if 'API' in config:
            if 'glm_key' in config['API']:
                try:
                    encrypted_glm_key = config['API']['glm_key'].encode()
                    glm_key = cipher_suite.decrypt(encrypted_glm_key).decode()
                except Exception as e:
                    print(f"解密GLM API Key失败: {e}")
            
            if 'deepseek_key' in config['API']:
                try:
                    encrypted_deepseek_key = config['API']['deepseek_key'].encode()
                    deepseek_key = cipher_suite.decrypt(encrypted_deepseek_key).decode()
                except Exception as e:
                    print(f"解密DeepSeek API Key失败: {e}")

        for i, (model, desc) in enumerate(models):
            radio = QPushButton(f"{model}({desc})")
            radio.setCheckable(True)
            radio.setAutoExclusive(True)
            radio.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: 2px solid #e0e7f0;
                    border-radius: 5px;
                    background-color: white;
                }
                QPushButton:checked {
                    border-color: #4CAF50;
                    background-color: #a0e6a0;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
            
            # 根据API密钥状态设置按钮是否可用
            if i < 4:  # GLM模型
                if not glm_key.strip():
                    radio.setDisabled(True)
            else:  # DeepSeek模型
                if not deepseek_key.strip():
                    radio.setDisabled(True)
                    
            self.model_buttons.append((radio, model))
            layout.addWidget(radio)

        # 确认按钮
        confirm_button = QPushButton("确认")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def get_selected_model(self):
        for button, model in self.model_buttons:
            if button.isChecked():
                return model
        return None

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 获取当前选择的模型名称
        try:
            if model_config.has_section('MODEL_CONFIG') and 'model' in model_config['MODEL_CONFIG']:
                encrypted_model = model_config['MODEL_CONFIG']['model']
                model = model_cipher_suite.decrypt(encrypted_model.encode()).decode()
                self.setWindowTitle(f"Nefelibata\u2003\u2003\u2003\u2003{model}")
                self.current_model = model
            else:
                self.setWindowTitle("Nefelibata\u2003\u2003\u2003\u2003No model selected")
                self.current_model = None
        except Exception as e:
            print(f"获取模型配置失败: {e}")
            self.setWindowTitle("Nefelibata")
            self.current_model = None
        self.setMinimumSize(1080, 720)
        self.setup_ui()
        self.ai_thread = None
        self.typing_animation = None
        self.api_key = self.get_api_key()
        self.timer = QTimer(self)
        self.dot_count = 0
        self.timer.timeout.connect(self.update_dot_animation)
        self.db = ChatDatabase()
        
        # 获取最新的会话ID或者创建新的
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT conversation_id FROM messages ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        self.conversation_id = result[0] if result else str(uuid.uuid4())
        
        # 加载历史消息
        history_messages = self.db.get_conversation_history(self.conversation_id)
        for message in history_messages:
            self.add_message(message['content'], align_right=(message['role'] == 'user'), message_id=message['id'])
        
        # 根据模型状态设置输入框和发送按钮的可用性
        self.input_box.setEnabled(self.current_model is not None)
        self.send_button.setEnabled(self.current_model is not None)
        if self.current_model is not None:
            self.input_box.setFocus()

    def setup_ui(self):
        # 设置主窗口样式
        self.setStyleSheet("""
                QWidget {
                    background-color: rgb(245,244,239);
                }
            """)

        # 设置窗口图标
        icon_path = resource_path('icon/icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"图标文件 {icon_path} 不存在。")

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        toolbar.addStretch()

        # API按钮
        self.api_button = QPushButton()
        try:
            svg_renderer = QSvgRenderer(resource_path('icon/key.svg'))
            pixmap = QPixmap(40, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            # 设置按钮图标
            self.api_button.setIcon(QIcon(pixmap))
            self.api_button.setIconSize(QSize(40, 40))
        except Exception as e:
            print(f"API图标加载失败: {e}")
        self.api_button.setFixedSize(40, 40)
        self.api_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 20px;
            }
        """)
        self.api_button.clicked.connect(self.show_api_key_dialog)
        toolbar.addWidget(self.api_button)

        # 设置按钮
        self.settings_button = QPushButton()
        try:
            svg_renderer = QSvgRenderer(resource_path('icon/setting.svg'))
            pixmap = QPixmap(36, 36)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            # 设置按钮图标
            self.settings_button.setIcon(QIcon(pixmap))
            self.settings_button.setIconSize(QSize(36, 36))
        except Exception as e:
            print(f"设置图标加载失败: {e}")
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 20px;
            }
        """)
        self.settings_button.clicked.connect(self.show_settings_dialog)
        toolbar.addWidget(self.settings_button)

        main_layout.addLayout(toolbar)

        # 聊天区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: 2px solid #c0c7d0;
                border-radius: 15px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(0, 0, 0, 0.4);
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 创建一个容器widget来存放所有消息
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setSpacing(10)
        self.message_layout.setContentsMargins(20, 20, 20, 20)
        self.message_layout.addStretch()
        self.scroll_area.setWidget(self.message_container)
        main_layout.addWidget(self.scroll_area)

        # 输入区域
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("请输入消息(enter换行)")
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e7f0;
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 14px;
                color: #2d3748;
                selection-background-color: #4CAF50;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        self.input_box.setFixedHeight(100)
        
        # 设置输入框的调色板
        palette = self.input_box.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor('#f0f0f0'))
        palette.setColor(QtGui.QPalette.ColorRole.PlaceholderText, QtGui.QColor('#999999'))
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor('#2d3748'))
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor('#f0f0f0'))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor('#2d3748'))
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor('#f0f0f0'))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor('#2d3748'))
        self.input_box.setPalette(palette)
        
        input_layout.addWidget(self.input_box)

        # 发送按钮
        self.send_button = QPushButton()
        self.send_button.setFixedSize(60, 60)
        try:
            self.send_icon = QIcon(resource_path('icon/send.svg'))
            self.stop_icon = QIcon(resource_path('icon/stop.svg'))
            send_pixmap = QPixmap(40, 40)
            send_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(send_pixmap)
            svg_renderer = QSvgRenderer(resource_path('icon/send.svg'))
            svg_renderer.render(painter)
            painter.end()
            # 设置按钮图标
            self.send_button.setIcon(QIcon(send_pixmap))
            self.send_button.setIconSize(QSize(40, 40))
        except Exception as e:
            print(f"发送/停止图标加载失败: {e}")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton[waiting="true"] {
                background-color: #ff4444;
            }
            QPushButton[waiting="true"]:hover {
                background-color: #ff0000;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        # 清除历史记录按钮
        clear_button = QPushButton()
        clear_button.setFixedSize(60, 60)
        try:
            svg_renderer = QSvgRenderer(resource_path('icon/clear.svg'))
            pixmap = QPixmap(40, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            # 设置按钮图标
            clear_button.setIcon(QIcon(pixmap))
            clear_button.setIconSize(QSize(40, 40))
        except Exception as e:
            print(f"清除图标加载失败: {e}")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 30px;
            }
        """)
        clear_button.clicked.connect(self.clear_history)
        input_layout.addWidget(clear_button)

        main_layout.addLayout(input_layout)

    def show_api_key_dialog(self):
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("设置API Key")
        dialog.setFixedSize(480, 300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: rgb(245,244,239);
            }
        """)

        # 创建布局
        layout = QVBoxLayout(dialog)

        # 创建GLM API Key输入框
        glm_label = QLabel("GLM API Key:")
        layout.addWidget(glm_label)
        self.glm_api_key_input = QTextEdit()
        self.glm_api_key_input.setPlaceholderText("请输入GLM API Key...")
        self.glm_api_key_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e7f0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(0, 0, 0, 0.4);
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.glm_api_key_input.setFixedHeight(50)
        layout.addWidget(self.glm_api_key_input)

        # 创建DeepSeek API Key输入框
        deepseek_label = QLabel("DeepSeek API Key:")
        layout.addWidget(deepseek_label)
        self.deepseek_api_key_input = QTextEdit()
        self.deepseek_api_key_input.setPlaceholderText("请输入DeepSeek API Key...")
        self.deepseek_api_key_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e7f0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.2);
                min-height: 30px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(0, 0, 0, 0.4);
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.deepseek_api_key_input.setFixedHeight(50)
        layout.addWidget(self.deepseek_api_key_input)

        # 加载现有的API Keys
        if 'API' in config:
            if 'glm_key' in config['API']:
                encrypted_glm_key = config['API']['glm_key'].encode()
                try:
                    glm_key = cipher_suite.decrypt(encrypted_glm_key).decode()
                    self.glm_api_key_input.setText(glm_key)
                except Exception as e:
                    print(f"解密GLM API Key失败: {e}")

            if 'deepseek_key' in config['API']:
                encrypted_deepseek_key = config['API']['deepseek_key'].encode()
                try:
                    deepseek_key = cipher_suite.decrypt(encrypted_deepseek_key).decode()
                    self.deepseek_api_key_input.setText(deepseek_key)
                except Exception as e:
                    print(f"解密DeepSeek API Key失败: {e}")

        # 创建保存按钮
        save_button = QPushButton("保存")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        save_button.clicked.connect(lambda: self.save_api_keys(dialog))
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # 显示对话框
        dialog.exec()

    def show_settings_dialog(self):
        # 显示模型选择对话框
        model_dialog = ModelSelectionDialog(self)
        if model_dialog.exec():
            selected_model = model_dialog.get_selected_model()
            if selected_model:
                print(f"用户选择的模型: {selected_model}")
                # 保存选择的模型到配置文件
                if not model_config.has_section('MODEL_CONFIG'):
                    model_config.add_section('MODEL_CONFIG')
                encrypted_model = model_cipher_suite.encrypt(selected_model.encode()).decode()
                model_config['MODEL_CONFIG']['model'] = encrypted_model
                with open(model_config_file, 'w') as f:
                    model_config.write(f)
                # 更新当前模型状态
                self.current_model = selected_model
                # 更新API密钥
                self.api_key = self.get_api_key()
                # 启用输入框和发送按钮
                self.input_box.setEnabled(True)
                self.send_button.setEnabled(True)
                self.input_box.setFocus()
                # 立即更新窗口标题
                self.setWindowTitle(f"Nefelibata\u2003\u2003\u2003\u2003{selected_model}")
    def add_message(self, content, align_right=False, message_id=None):
        # 创建消息容器
        message_widget = QWidget()
        message_widget.message_id = message_id  # 存储消息ID
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(5)
        
        # 创建消息内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建消息标签
        message_label = QLabel(content)
        message_label.setWordWrap(True)
        
        # 获取字体度量信息
        font_metrics = QtGui.QFontMetrics(message_label.font())
        # 设置最大宽度
        max_width = 960  
        
        # 处理文本自动换行
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if font_metrics.horizontalAdvance(line) <= max_width:
                formatted_lines.append(line)
            else:
                current_line = ''
                words = line.split(' ')
                
                for word in words:
                    test_line = current_line + (' ' if current_line else '') + word
                    if font_metrics.horizontalAdvance(test_line) <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            formatted_lines.append(current_line)
                        current_line = word
                
                if current_line:
                    formatted_lines.append(current_line)
        
        # 设置处理后的文本
        message_label.setText('\n'.join(formatted_lines))
        message_label.setMaximumWidth(max_width)
        message_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        message_label.setStyleSheet(f"""
            QLabel {{
                background-color: {'#a0e6a0' if align_right else 'white'};
                border-radius: 15px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
        
        # 根据发送者调整消息位置
        if align_right:
            content_layout.addStretch()
        content_layout.addWidget(message_label)
        if not align_right:
            content_layout.addStretch()
        
        message_layout.addWidget(content_widget)
        
        # 创建复制按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 设置按钮之间的间距为2像素
        button_layout.setSpacing(2)  
        
        # 创建复制按钮
        copy_button = QPushButton()
        copy_button.setFixedSize(24, 24)
        try:
            copy_button.setIcon(QIcon(resource_path('icon/copy.svg')))
        except Exception as e:
            print(f"复制图标加载失败: {e}")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        
        # 设置复制功能
        copy_button.clicked.connect(lambda: self.copy_message_content(content))
        
        # 创建删除按钮
        delete_button = QPushButton()
        delete_button.setFixedSize(24, 24)
        try:
            delete_button.setIcon(QIcon(resource_path('icon/delete.svg')))
        except Exception as e:
            print(f"删除图标加载失败: {e}")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        
        # 设置删除功能
        delete_button.clicked.connect(lambda: self.delete_message(message_widget))
        
        # 根据消息位置调整按钮位置
        if align_right:
            button_layout.addStretch()
        button_layout.addWidget(copy_button)
        button_layout.addWidget(delete_button)
        if not align_right:
            button_layout.addStretch()
        
        message_layout.addWidget(button_widget)
        
        # 将消息添加到消息容器中
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
        # 使用QTimer延迟执行滚动动画，确保布局更新完成
        QTimer.singleShot(100, lambda: self.scroll_to_bottom())
    
    def scroll_to_bottom(self):
        scroll_bar = self.scroll_area.verticalScrollBar()
        target_value = scroll_bar.maximum()
        current_value = scroll_bar.value()
        
        # 创建动画
        self.scroll_animation = QPropertyAnimation(scroll_bar, b"value")
        
        # 根据滚动距离动态计算动画时长
        distance = abs(target_value - current_value)
        # 基础动画时长
        base_duration = 1200  
        # 使用对数函数调整动画时长，确保长距离滚动不会太慢
        duration = min(base_duration, int(base_duration * (1 + math.log10(1 + distance/100))))
        
        # 使用动态计算的时长
        self.scroll_animation.setDuration(duration)  
        self.scroll_animation.setStartValue(current_value)
        self.scroll_animation.setEndValue(target_value)
        # 使用OutCubic曲线实现更流畅的减速效果
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)  
        self.scroll_animation.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def send_message(self):
        if self.send_button.property("waiting"):
            # 如果正在等待AI回复，点击按钮则中断
            if self.ai_thread and self.ai_thread.isRunning():
                self.ai_thread.terminate()
                self.ai_thread.wait()
                self.timer.stop()
                self.input_box.setDisabled(False)
                self.input_box.clear()
                self.input_box.setStyleSheet("""
                    QTextEdit {
                        background-color: #f5f5f5;
                        border: 2px solid #e0e7f0;
                        border-radius: 15px;
                        padding: 10px;
                        font-size: 14px;
                    }
                    QTextEdit:focus {
                        border: 2px solid #4CAF50;
                    }
                    QTextEdit:disabled {
                        background-color: #f5f5f5;
                        border: 2px solid #e0e7f0;
                    }
                """)
                self.send_button.setIcon(self.send_icon)
                self.send_button.setProperty("waiting", False)
                self.send_button.setStyleSheet(self.send_button.styleSheet())
                
                # 显示中断提示
                self.show_interrupt_toast()
                return

        # 检查当前模型对应的API密钥是否存在
        api_key = self.get_api_key()
        if not api_key:
            # 创建自定义提示窗口
            toast = QDialog(self)
            toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
            toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # 创建提示文本
            label = QLabel("无API Key", toast)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    padding: 10px 15px;
                    border-radius: 6px;
                    background-color: rgba(0, 0, 0, 0.8);
                    font-size: 14px;
                    font-weight: 500;
                }
            """)
            
            # 设置布局
            layout = QVBoxLayout(toast)
            layout.addWidget(label)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # 计算位置（相对于父窗口居中显示）
            parent_geometry = self.geometry()
            toast_width = 120
            toast_height = 45
            x = parent_geometry.x() + (parent_geometry.width() - toast_width) // 2
            y = parent_geometry.y() + (parent_geometry.height() - toast_height) // 2
            toast.setGeometry(x, y, toast_width, toast_height)
            
            # 显示提示窗口
            toast.show()
            
            # 1秒后自动关闭
            QTimer.singleShot(1000, toast.close)
            return

        text = self.input_box.toPlainText().strip()
        if not text:
            # 如果输入框为空，触发抖动动画
            self.show_input_hint()
            return
            
        # 保存用户消息到数据库
        message_id = self.db.save_message(text, 'user', self.conversation_id)
        self.add_message(text, align_right=True, message_id=message_id)
        self.input_box.setDisabled(True)
        self.timer.start(500)  # 启动等待动画
        # 设置按钮为停止状态
        self.send_button.setProperty("waiting", True)
        self.send_button.setIcon(self.stop_icon)
        self.send_button.setStyleSheet(self.send_button.styleSheet())
        self.get_ai_response(text)

    def show_interrupt_toast(self):
        # 创建自定义提示窗口
        toast = QDialog(self)
        toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建提示文本
        label = QLabel("已中断", toast)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                background-color: rgba(0, 0, 0, 0.8);
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # 设置布局
        layout = QVBoxLayout(toast)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算位置（居中显示）
        screen_geometry = QApplication.primaryScreen().geometry()
        toast_width = 120
        toast_height = 45
        x = (screen_geometry.width() - toast_width) // 2
        y = (screen_geometry.height() - toast_height) // 2
        toast.setGeometry(x, y, toast_width, toast_height)
        
        # 显示提示窗口
        toast.show()
        
        # 1秒后自动关闭
        QTimer.singleShot(1000, toast.close)

    def get_ai_response(self, text):
        # 获取当前选择的模型
        try:
            if model_config.has_section('MODEL_CONFIG') and 'model' in model_config['MODEL_CONFIG']:
                encrypted_model = model_config['MODEL_CONFIG']['model']
                model = model_cipher_suite.decrypt(encrypted_model.encode()).decode()
                print(f"当前发送的模型: {model}")
            else:
                # 默认模型
                model = "glm-4-flash"  
        except Exception as e:
            print(f"获取模型配置失败: {e}")
            # 如果获取失败，使用默认模型
            model = "glm-4-flash"  

        # 获取历史消息
        history_messages = self.db.get_conversation_history(self.conversation_id)

        # 创建并启动AI线程
        self.ai_thread = AIChatThread(text, self.api_key, history_messages=history_messages, model=model)
        self.ai_thread.response_received.connect(self.handle_ai_response)
        self.ai_thread.error_occurred.connect(self.handle_error)
        self.ai_thread.start()

    def handle_ai_response(self, text):
        self.timer.stop()
        self.input_box.setDisabled(False)
        self.input_box.clear()
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e7f0;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)

        self.send_button.setProperty("waiting", False)
        self.send_button.setIcon(self.send_icon)
        self.send_button.setStyleSheet(self.send_button.styleSheet())
        
        # 保存AI响应并获取消息ID
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, sender, conversation_id) VALUES (?, ?, ?)',
                      (text, "ai", self.conversation_id))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.add_message(text, align_right=False, message_id=message_id)

    def handle_error(self, message):
        self.timer.stop()
        self.input_box.setDisabled(False)
        self.input_box.clear()
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e7f0;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        self.send_button.setProperty("waiting", False)
        self.send_button.setIcon(self.send_icon)  # 更新发送按钮图标
        self.send_button.setStyleSheet(self.send_button.styleSheet())
        self.add_message(f"错误: {message}", align_right=False)

    def show_input_hint(self):
        # 显示提示信息
        self.show_toast("消息不能为空！")

    def delete_message(self, message_widget):
        # 如果消息有ID，从数据库中删除
        if hasattr(message_widget, 'message_id') and message_widget.message_id is not None:
            self.db.delete_message(message_widget.message_id)
        # 从消息容器中移除消息组件
        self.message_layout.removeWidget(message_widget)
        message_widget.deleteLater()

    def copy_message_content(self, content):
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        
        # 创建自定义提示窗口
        toast = QDialog(self)
        toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建提示文本
        label = QLabel("已复制", toast)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                background-color: rgba(0, 0, 0, 0.8);
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # 设置布局
        layout = QVBoxLayout(toast)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算位置（居中显示）
        screen_geometry = QApplication.primaryScreen().geometry()
        toast_width = 120
        toast_height = 45
        x = (screen_geometry.width() - toast_width) // 2
        y = (screen_geometry.height() - toast_height) // 2
        toast.setGeometry(x, y, toast_width, toast_height)
        
        # 显示提示窗口
        toast.show()
        
        # 1秒后自动关闭
        QTimer.singleShot(1000, toast.close)
    def show_toast(self, message):
        # 创建自定义提示窗口
        toast = QDialog(self)
        toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建提示文本
        label = QLabel(message, toast)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                background-color: rgba(0, 0, 0, 0.8);
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # 设置布局
        layout = QVBoxLayout(toast)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算位置（相对于父窗口居中显示）
        parent_geometry = self.geometry()
        toast_width = max(120, label.sizeHint().width() + 30)
        toast_height = 45
        x = parent_geometry.x() + (parent_geometry.width() - toast_width) // 2
        y = parent_geometry.y() + (parent_geometry.height() - toast_height) // 2
        toast.setGeometry(x, y, toast_width, toast_height)
        
        # 显示提示窗口
        toast.show()
        
        # 1秒后自动关闭
        QTimer.singleShot(1000, toast.close)
    def save_api_key(self, dialog):
        api_key = self.api_key_input.toPlainText().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "API Key不能为空！")
            return

        # 加密并保存API Key
        if not config.has_section('API'):
            config.add_section('API')
        encrypted_key = cipher_suite.encrypt(api_key.encode()).decode()
        config['API']['key'] = encrypted_key
        with open(config_file, 'w') as f:
            config.write(f)

        self.api_key = api_key
        dialog.accept()
        QMessageBox.information(self, "成功", "API Key已保存！")
    def save_api_keys(self, dialog):
        # 获取输入的API Keys
        glm_key = self.glm_api_key_input.toPlainText().strip()
        deepseek_key = self.deepseek_api_key_input.toPlainText().strip()

        # 检查是否两个API Key都为空
        if not glm_key and not deepseek_key:
            # 重置窗口标题为Nefelibata
            self.setWindowTitle("Nefelibata\u2003\u2003\u2003\u2003No model selected")
            self.current_model = None
            # 禁用输入框和发送按钮
            self.input_box.setEnabled(False)
            self.send_button.setEnabled(False)
            # 清除模型配置
            if model_config.has_section('MODEL_CONFIG'):
                model_config.remove_section('MODEL_CONFIG')
                with open(model_config_file, 'w') as f:
                    model_config.write(f)

        # 获取当前选择的模型名称
        current_model = ""
        try:
            if model_config.has_section('MODEL_CONFIG') and 'model' in model_config['MODEL_CONFIG']:
                encrypted_model = model_config['MODEL_CONFIG']['model']
                current_model = model_cipher_suite.decrypt(encrypted_model.encode()).decode()
            else:
                current_model = "glm-4-flash"
        except Exception as e:
            print(f"获取模型配置失败: {e}")
            current_model = "glm-4-flash"

        # 验证API Keys格式
        glm_valid = self.validate_api_key(glm_key, "glm-4")
        deepseek_valid = self.validate_api_key(deepseek_key, "deepseek-ai")

        # 创建自定义提示窗口，设置父窗口为dialog确保显示在其上层
        toast = QDialog(dialog)
        toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建提示文本
        label = QLabel("API格式错误" if not glm_valid or not deepseek_valid else "API保存成功", toast)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                background-color: rgba(0, 0, 0, 0.8);
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # 设置布局
        layout = QVBoxLayout(toast)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算位置（相对于父窗口居中显示）
        dialog_geometry = dialog.geometry()
        toast_width = 120
        toast_height = 45
        x = dialog_geometry.x() + (dialog_geometry.width() - toast_width) // 2
        y = dialog_geometry.y() + (dialog_geometry.height() - toast_height) // 2
        toast.setGeometry(x, y, toast_width, toast_height)
        
        # 显示提示窗口
        toast.show()
        
        # 1秒后自动关闭
        QTimer.singleShot(1000, toast.close)
        
        # 如果格式无效，直接返回
        if not glm_valid or not deepseek_valid:
            return

        # 加密API Keys
        try:
            encrypted_glm_key = cipher_suite.encrypt(glm_key.encode()).decode()
            encrypted_deepseek_key = cipher_suite.encrypt(deepseek_key.encode()).decode()

            # 确保config有API部分
            if 'API' not in config:
                config['API'] = {}

            # 保存加密后的API Keys
            config['API']['glm_key'] = encrypted_glm_key
            config['API']['deepseek_key'] = encrypted_deepseek_key

            # 写入配置文件
            with open(config_file, 'w') as f:
                config.write(f)

            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存API Keys失败: {str(e)}")

    def validate_api_key(self, api_key, model_type):
        if not api_key:  # 如果API密钥为空，返回True（允许清空API密钥）
            return True
            
        if model_type == "glm-4":
            # GLM API密钥格式验证
            return bool(re.match(r'^[a-zA-Z0-9]{32}\.[a-zA-Z0-9]{16}$', api_key))
        elif model_type == "deepseek-ai":
            # DeepSeek API密钥格式验证
            return bool(re.match(r'^sk-[a-zA-Z0-9]{48}$', api_key))
        return False

    def get_api_key(self):
        try:
            if 'API' in config:
                # 获取当前选择的模型
                current_model = ""
                if model_config.has_section('MODEL_CONFIG') and 'model' in model_config['MODEL_CONFIG']:
                    encrypted_model = model_config['MODEL_CONFIG']['model']
                    current_model = model_cipher_suite.decrypt(encrypted_model.encode()).decode()
                else:
                    current_model = "glm-4-flash"

                # 根据模型类型选择对应的API Key
                api_key = ""
                if current_model.startswith("deepseek-ai") or current_model.startswith("Pro/deepseek-ai"):
                    if 'deepseek_key' in config['API'] and config['API']['deepseek_key']:
                        encrypted_key = config['API']['deepseek_key'].encode()
                        api_key = cipher_suite.decrypt(encrypted_key).decode()
                else:
                    if 'glm_key' in config['API'] and config['API']['glm_key']:
                        encrypted_key = config['API']['glm_key'].encode()
                        api_key = cipher_suite.decrypt(encrypted_key).decode()
                
                return api_key
        except Exception as e:
            print(f"获取API Key失败: {e}")
        return ""
    def update_dot_animation(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = '.' * self.dot_count
        self.input_box.setPlainText(f"等待ai回复{dots}")

    def clear_history(self):
        # 创建自定义确认对话框
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dialog.setFixedSize(280, 180)
        
        # 创建主布局
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建内容容器
        content_widget = QWidget(dialog)
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)  # 调整间距
        content_layout.setContentsMargins(25, 25, 25, 25)  # 调整内边距
        
        # 创建提示文本
        message_label = QLabel("确定要清除所有聊天记录吗？\n此操作不可恢复。")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                font-size: 16px;
            }
        """)
        content_layout.addWidget(message_label)
        
        # 创建按钮容器
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(15)
        
        # 创建取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.setFixedSize(100, 40)
        cancel_button.clicked.connect(dialog.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 20px;
                color: #2d3748;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # 创建确认按钮
        confirm_button = QPushButton("确认清除")
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(dialog.accept)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(confirm_button)
        button_layout.addStretch()
        content_layout.addWidget(button_widget)
        
        # 设置内容容器样式
        content_widget.setStyleSheet("""
            #contentWidget {
                background-color: rgb(245,244,239);
                border: 1px solid #d0d0d0;
                border-radius: 15px;
            }
        """)
        
        layout.addWidget(content_widget)
        
        # 显示对话框并处理结果
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 关闭数据库连接
            if hasattr(self.db, '_conn') and self.db._conn:
                self.db._conn.close()
            
            # 删除数据库文件
            if os.path.exists(self.db.db_path):
                os.remove(self.db.db_path)
            
            # 重新初始化数据库
            self.db.init_database()
            
            # 清除界面上的所有消息
            while self.message_layout.count() > 1:  # 保留最后一个stretch
                item = self.message_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # 显示已清空提示
            toast = QDialog(self)
            toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
            toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # 创建提示文本
            label = QLabel("已清空", toast)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    padding: 10px 15px;
                    border-radius: 6px;
                    background-color: rgba(0, 0, 0, 0.8);
                    font-size: 14px;
                    font-weight: 500;
                }
            """)
            
            # 设置布局
            layout = QVBoxLayout(toast)
            layout.addWidget(label)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # 计算位置（居中显示）
            screen_geometry = QApplication.primaryScreen().geometry()
            toast_width = 120
            toast_height = 45
            x = (screen_geometry.width() - toast_width) // 2
            y = (screen_geometry.height() - toast_height) // 2
            toast.setGeometry(x, y, toast_width, toast_height)
            
            # 显示提示窗口
            toast.show()
            
            # 1秒后自动关闭
            QTimer.singleShot(1000, toast.close)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置全局字体
    if sys.platform == 'darwin':  # macOS
        font = QFont("PingFang SC", 10)
    else:  # Windows 和其他系统
        font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = ChatWindow()
    window.show()
    sys.exit(app.exec())