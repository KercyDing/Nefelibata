"""
对话框组件
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QFormLayout, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from utils.resources import resource_path
from .styles import StyleManager


class ModelSelectionDialog(QDialog):
    """模型选择对话框"""    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("选择模型")
        self.setFixedSize(400, 580)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowMaximizeButtonHint)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # GLM模型区域
        glm_title = QLabel("智谱AI模型")
        glm_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 5px 0px;
            }
        """)
        layout.addWidget(glm_title)
        
        # GLM模型选项
        glm_models = [
            ("glm-z1-flash", "免费推理模型"),
            ("glm-z1-airx", "极速推理模型"), 
            ("glm-z1-air", "高性价比推理模型"),
            ("glm-4-plus", "旗舰级别模型")
        ]
        
        # SiliconFlow模型区域
        sf_title = QLabel("SiliconFlow模型")
        sf_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                padding: 15px 0px 5px 0px;
            }
        """)
        
        # SiliconFlow模型选项
        sf_models = [
            ("deepseek-ai/DeepSeek-V3", "快速精准推理"),
            ("deepseek-ai/DeepSeek-R1", "深度推理模型"),
            ("Qwen/Qwen3-235B-A22B", "超大上下文模型")
        ]

        self.model_buttons = []
        
        # 获取API密钥状态
        glm_key = self.config_manager.get_api_key("glm")
        siliconflow_key = self.config_manager.get_api_key("deepseek")

        # 添加GLM模型按钮
        for model, desc in glm_models:
            radio = QPushButton(f"{model} - {desc}")
            radio.setCheckable(True)
            radio.setAutoExclusive(True)
            radio.setFixedHeight(40)
            radio.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 13px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:checked {
                    background-color: #4caf50;
                    border-color: #4caf50;
                    color: white;
                }
                QPushButton:disabled {
                    background-color: #f8f9fa;
                    color: #6c757d;
                    border-color: #dee2e6;
                }
            """)
            
            if not glm_key.strip():
                radio.setDisabled(True)
                radio.setToolTip("请先设置GLM API Key")
                    
            self.model_buttons.append((radio, model))
            layout.addWidget(radio)

        layout.addWidget(sf_title)

        # 添加SiliconFlow模型按钮
        for model, desc in sf_models:
            radio = QPushButton(f"{model} - {desc}")
            radio.setCheckable(True)
            radio.setAutoExclusive(True)
            radio.setFixedHeight(40)
            radio.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 8px 12px;
                    text-align: left;
                    font-size: 13px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #adb5bd;
                }
                QPushButton:checked {
                    background-color: #4caf50;
                    border-color: #4caf50;
                    color: white;
                }
                QPushButton:disabled {
                    background-color: #f8f9fa;
                    color: #6c757d;
                    border-color: #dee2e6;
                }
            """)
            if not siliconflow_key.strip():
                radio.setDisabled(True)
                radio.setToolTip("请先设置SiliconFlow API Key")                    
            self.model_buttons.append((radio, model))
            layout.addWidget(radio)

        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        # 设置API Key按钮
        api_button = QPushButton("设置API Key")
        api_button.setFixedSize(100, 35)
        api_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        api_button.clicked.connect(self._open_api_dialog)
        
        # 确认按钮
        confirm_button = QPushButton("确认选择")
        confirm_button.setFixedSize(100, 35)
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(api_button)
        button_layout.addStretch()
        button_layout.addWidget(confirm_button)
        
        layout.addLayout(button_layout)    
        
    def _open_api_dialog(self):
        """打开API Key设置对话框"""
        dialog = APIKeyDialog(self.config_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 刷新按钮状态
            self._refresh_button_states()

    def _refresh_button_states(self):
        """刷新按钮状态"""
        glm_key = self.config_manager.get_api_key("glm")
        siliconflow_key = self.config_manager.get_api_key("deepseek")
        
        for button, model in self.model_buttons:
            if model.startswith("glm-"):
                button.setEnabled(bool(glm_key.strip()))
            else:
                button.setEnabled(bool(siliconflow_key.strip()))

    def get_selected_model(self):
        """获取选择的模型"""
        for button, model in self.model_buttons:
            if button.isChecked():
                return model
        return None


class APIKeyDialog(QDialog):
    """API密钥设置对话框"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("设置API Key")
        self.setFixedSize(480, 300)
        self.setStyleSheet(StyleManager.get_dialog_style())
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)

        # 创建GLM API Key输入框
        glm_label = QLabel("GLM API Key:")
        layout.addWidget(glm_label)
        self.glm_api_key_input = QTextEdit()
        self.glm_api_key_input.setPlaceholderText("请输入GLM API Key...")
        self.glm_api_key_input.setStyleSheet(StyleManager.get_api_input_style())
        self.glm_api_key_input.setFixedHeight(50)
        layout.addWidget(self.glm_api_key_input)

        # 创建SiliconFlow API Key输入框
        deepseek_label = QLabel("SiliconFlow API Key:")
        layout.addWidget(deepseek_label)
        self.deepseek_api_key_input = QTextEdit()
        self.deepseek_api_key_input.setPlaceholderText("请输入SiliconFlow API Key...")
        self.deepseek_api_key_input.setStyleSheet(StyleManager.get_api_input_style())
        self.deepseek_api_key_input.setFixedHeight(50)
        layout.addWidget(self.deepseek_api_key_input)

        # 加载现有的API Keys
        self._load_existing_keys()

        # 创建保存按钮
        save_button = QPushButton("保存")
        save_button.setStyleSheet(StyleManager.get_primary_button_style())
        save_button.clicked.connect(self._save_keys)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)
    def _load_existing_keys(self):
        """加载现有的API密钥"""
        glm_key = self.config_manager.get_api_key("glm")
        if glm_key:
            self.glm_api_key_input.setText(glm_key)
        
        siliconflow_key = self.config_manager.get_api_key("deepseek")
        if siliconflow_key:
            self.deepseek_api_key_input.setText(siliconflow_key)

    def _save_keys(self):
        """保存API密钥"""
        glm_key = self.glm_api_key_input.toPlainText().strip()
        siliconflow_key = self.deepseek_api_key_input.toPlainText().strip()
        
        # 验证API Keys格式
        glm_valid = self.config_manager.validate_api_key(glm_key, "glm-4")
        siliconflow_valid = self.config_manager.validate_api_key(siliconflow_key, "deepseek-ai")
        
        if not glm_valid or not siliconflow_valid:
            # 显示错误提示
            from .widgets import ToastWidget
            ToastWidget("API格式错误", self).show()
            return
        
        # 保存密钥
        self.config_manager.save_api_key("glm", glm_key)
        self.config_manager.save_api_key("deepseek", siliconflow_key)
        
        # 显示成功提示
        from .widgets import ToastWidget
        ToastWidget("API保存成功", self).show()
        
        # 关闭对话框
        self.accept()


class ConfirmDialog(QDialog):
    """确认对话框"""
    
    def __init__(self, message: str, title: str = "确认", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 180)
        self.setup_ui(message, title)
    
    def setup_ui(self, message: str, title: str):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建内容容器
        content_widget = QWidget(self)
        content_widget.setObjectName("contentWidget")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # 创建提示文本
        message_label = QLabel(message)
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
        cancel_button.clicked.connect(self.reject)
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
        confirm_button = QPushButton("确认")
        confirm_button.setFixedSize(100, 40)
        confirm_button.clicked.connect(self.accept)
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
