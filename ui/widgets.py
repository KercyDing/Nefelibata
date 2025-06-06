"""
自定义控件
"""
from PyQt6.QtWidgets import QTextEdit, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFontMetrics
from PyQt6 import QtGui
from utils.resources import resource_path
from .styles import StyleManager


class CustomTextEdit(QTextEdit):
    """自定义文本编辑器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift+Enter 换行
                super().keyPressEvent(event)
            else:
                # Enter 发送消息
                self.parent.send_message()
        else:
            super().keyPressEvent(event)


class MessageWidget(QWidget):
    """消息组件"""
    def __init__(self, content: str, align_right: bool = False, message_id: int = None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.message_id = message_id
        # 清理消息内容，去除开头和结尾的空行和空白字符
        self.content = content.strip() if content else ""
        self.align_right = align_right
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        message_layout = QVBoxLayout(self)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(5)
        
        # 创建消息内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建消息标签
        message_label = QLabel(self.content)
        message_label.setWordWrap(True)
        
        # 处理文本自动换行
        self._format_message_text(message_label)
        
        # 根据发送者调整消息位置
        if self.align_right:
            content_layout.addStretch()
        content_layout.addWidget(message_label)
        if not self.align_right:
            content_layout.addStretch()
        
        message_layout.addWidget(content_widget)
        
        # 创建按钮区域
        self._create_button_area(message_layout)
    
    def _format_message_text(self, message_label: QLabel):
        """格式化消息文本"""
        font_metrics = QFontMetrics(message_label.font())
        max_width = 960
        
        lines = self.content.split('\n')
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
                background-color: {'#a0e6a0' if self.align_right else 'white'};
                border-radius: 15px;
                padding: 12px;
                font-size: 14px;
            }}
        """)
    
    def _create_button_area(self, message_layout: QVBoxLayout):
        """创建按钮区域"""
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)
        
        # 创建复制按钮
        copy_button = QPushButton()
        copy_button.setFixedSize(24, 24)
        try:
            copy_button.setIcon(QIcon(resource_path('icon/copy.svg')))
        except Exception as e:
            print(f"复制图标加载失败: {e}")
        copy_button.setStyleSheet(StyleManager.get_message_button_style())
        copy_button.clicked.connect(self._copy_message)
        
        # 创建删除按钮
        delete_button = QPushButton()
        delete_button.setFixedSize(24, 24)
        try:
            delete_button.setIcon(QIcon(resource_path('icon/delete.svg')))
        except Exception as e:
            print(f"删除图标加载失败: {e}")
        delete_button.setStyleSheet(StyleManager.get_message_button_style())
        delete_button.clicked.connect(self._delete_message)
        
        # 根据消息位置调整按钮位置
        if self.align_right:
            button_layout.addStretch()
        button_layout.addWidget(copy_button)
        button_layout.addWidget(delete_button)
        if not self.align_right:
            button_layout.addStretch()
        
        message_layout.addWidget(button_widget)
    
    def _copy_message(self):
        """复制消息内容"""
        if self.parent and hasattr(self.parent, 'copy_message_content'):
            self.parent.copy_message_content(self.content)
    
    def _delete_message(self):
        """删除消息"""
        if self.parent and hasattr(self.parent, 'delete_message'):
            self.parent.delete_message(self)


class ToastWidget(QDialog):
    """提示信息组件"""
    
    def __init__(self, message: str, parent=None, duration: int = 1000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建提示文本
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(StyleManager.get_toast_style())
        
        # 设置布局
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算位置和大小
        self._calculate_geometry(label, parent)
        
        # 定时关闭
        QTimer.singleShot(duration, self.close)
    
    def _calculate_geometry(self, label: QLabel, parent):
        """计算几何位置"""
        toast_width = max(120, label.sizeHint().width() + 30)
        toast_height = 45
        
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - toast_width) // 2
            y = parent_geometry.y() + (parent_geometry.height() - toast_height) // 2
        else:
            # 居中显示
            from PyQt6.QtWidgets import QApplication
            screen_geometry = QApplication.primaryScreen().geometry()
            x = (screen_geometry.width() - toast_width) // 2
            y = (screen_geometry.height() - toast_height) // 2
        
        self.setGeometry(x, y, toast_width, toast_height)
