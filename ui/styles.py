"""
样式管理器
"""


class StyleManager:
    """UI样式管理器"""
    
    @staticmethod
    def get_main_window_style() -> str:
        """主窗口样式"""
        return """
            QWidget {
                background-color: rgb(245,244,239);
            }
        """
    
    @staticmethod
    def get_dialog_style() -> str:
        """对话框样式"""
        return """
            QDialog {
                background-color: rgb(245,244,239);
            }
        """
    @staticmethod
    def get_input_style() -> str:
        """输入框样式"""
        return """
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
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                margin: 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(76, 175, 80, 0.6);
                min-height: 20px;
                border-radius: 4px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(76, 175, 80, 0.8);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(76, 175, 80, 1.0);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """
    
    @staticmethod
    def get_api_input_style() -> str:
        """API密钥输入框样式"""
        return """
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
        """
    
    @staticmethod
    def get_button_style() -> str:
        """按钮样式"""
        return """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 20px;
            }
        """
    @staticmethod
    def get_send_button_style() -> str:
        """发送按钮样式"""
        return """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QPushButton[waiting="true"] {
                background-color: #F58282;
                border-radius: 25px;
            }
            QPushButton[waiting="true"]:hover {
                background-color: #FC5454;
            }
        """
    
    @staticmethod
    def get_primary_button_style() -> str:
        """主要按钮样式"""
        return """
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
        """
    
    @staticmethod
    def get_model_button_style() -> str:
        """模型选择按钮样式"""
        return """
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
        """
    
    @staticmethod
    def get_scroll_area_style() -> str:
        """滚动区域样式"""
        return """
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
        """
    
    @staticmethod
    def get_toast_style() -> str:
        """提示框样式"""
        return """
            QLabel {
                color: white;
                padding: 10px 15px;
                border-radius: 6px;
                background-color: rgba(0, 0, 0, 0.8);
                font-size: 14px;
                font-weight: 500;
            }
        """
    
    @staticmethod
    def get_message_button_style() -> str:
        """消息按钮样式"""
        return """
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """
