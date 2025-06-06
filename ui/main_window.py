"""
主聊天窗口
"""
import sys
import os
import sqlite3
import uuid
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QScrollArea, QApplication, QSizePolicy, QDialog, QLabel)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

from utils.resources import resource_path, get_config_paths, get_icon_path
from core.config_manager import ConfigManager
from core.ai_client import AIChatThread, AIStreamThread
from .styles import StyleManager
from .widgets import CustomTextEdit, MessageWidget, ToastWidget
from .dialogs import APIKeyDialog, ModelSelectionDialog, ConfirmDialog
from chat_db import ChatDatabase


class ChatWindow(QWidget):
    """主聊天窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化配置管理器
        config_paths = get_config_paths()
        self.config_manager = ConfigManager(config_paths)
        
        # 初始化数据库
        self.db = ChatDatabase()
          # 初始化状态
        self.ai_thread = None
        self.typing_animation = None
        self.timer = QTimer(self)
        self.dot_count = 0
        self.timer.timeout.connect(self.update_dot_animation)
        
        # 流式输出相关状态
        self.current_ai_message_widget = None  # 当前AI消息组件引用
        self.full_ai_response = ""  # 存储完整的AI响应文本
        
        # 获取当前模型和会话
        self.current_model = self.config_manager.get_current_model()
        self.conversation_id = self._get_or_create_conversation()
        
        # 设置窗口
        self._setup_window()
        self.setup_ui()
        
        # 加载历史消息
        self._load_history_messages()
          # 根据模型状态设置输入框和发送按钮的可用性
        self._update_ui_state()
    
    def _update_model_label(self):
        """更新模型名称标签"""
        if self.current_model:
            self.model_label.setText(self.current_model)
            self.model_label.setVisible(True)
        else:
            self.model_label.setText("未选择模型")
            self.model_label.setVisible(True)
    def _setup_window(self):
        """设置窗口属性"""
        self.setMinimumSize(1080, 720)
        self.setStyleSheet(StyleManager.get_main_window_style())
        
        # 设置窗口标题（仅显示应用名称）
        self.setWindowTitle("Nefelibata")
        
        # 设置窗口图标
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"图标文件 {icon_path} 不存在。")
    
    def _get_or_create_conversation(self):
        """获取或创建会话ID"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT conversation_id FROM messages ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else str(uuid.uuid4())
    
    def _load_history_messages(self):
        """加载历史消息"""
        history_messages = self.db.get_conversation_history(self.conversation_id)
        for message in history_messages:
            self.add_message(
                message['content'], 
                align_right=(message['role'] == 'user'), 
                message_id=message['id']
            )
    
    def _update_ui_state(self):
        """更新UI状态"""
        has_model = self.current_model is not None
        self.input_box.setEnabled(has_model)
        self.send_button.setEnabled(has_model)
        if has_model:
            self.input_box.setFocus()

    def setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 创建顶部工具栏
        self._create_toolbar(main_layout)
        
        # 创建聊天区域
        self._create_chat_area(main_layout)
        
        # 创建输入区域
        self._create_input_area(main_layout)

    def _create_toolbar(self, main_layout: QVBoxLayout):
        """创建顶部工具栏"""
        toolbar = QHBoxLayout()
        
        # 左侧区域（空白，用于平衡右侧按钮）
        left_spacer = QHBoxLayout()
        left_spacer.addStretch()
        # 为了平衡右侧的两个按钮，左侧也留出相同的空间
        left_spacer.setFixedSize = lambda: None  # 占位
        toolbar.addLayout(left_spacer, 1)  # 权重为1

        # 中央区域 - 模型名称标签
        center_layout = QHBoxLayout()
        self.model_label = QLabel()
        self.model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_label.setStyleSheet("""
            QLabel {
                color: #2d3748;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 20px;
                background-color: rgba(76, 175, 80, 0.1);
                border: 1px solid rgba(76, 175, 80, 0.3);
                border-radius: 20px;
                margin: 0 20px;
            }
        """)
        self._update_model_label()
        center_layout.addWidget(self.model_label)
        toolbar.addLayout(center_layout, 1)  # 权重为1

        # 右侧区域 - 按钮组
        right_layout = QHBoxLayout()
        right_layout.addStretch()
        
        # API按钮
        self.api_button = self._create_icon_button('icon/key.svg', 40, self.show_api_key_dialog)
        right_layout.addWidget(self.api_button)

        # 设置按钮
        self.settings_button = self._create_icon_button('icon/setting.svg', 36, self.show_settings_dialog)
        right_layout.addWidget(self.settings_button)
        
        toolbar.addLayout(right_layout, 1)  # 权重为1

        main_layout.addLayout(toolbar)
    
    def _create_icon_button(self, icon_path: str, size: int, callback) -> QPushButton:
        """创建图标按钮"""
        button = QPushButton()
        try:
            svg_renderer = QSvgRenderer(resource_path(icon_path))
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            svg_renderer.render(painter)
            painter.end()
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(size, size))
        except Exception as e:
            print(f"图标加载失败 {icon_path}: {e}")
        
        button.setFixedSize(40, 40)
        button.setStyleSheet(StyleManager.get_button_style())
        button.clicked.connect(callback)
        return button
    
    def _create_chat_area(self, main_layout: QVBoxLayout):
        """创建聊天区域"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(StyleManager.get_scroll_area_style())
        
        # 创建消息容器
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setSpacing(10)
        self.message_layout.setContentsMargins(20, 20, 20, 20)
        self.message_layout.addStretch()
        self.scroll_area.setWidget(self.message_container)
        main_layout.addWidget(self.scroll_area)
    
    def _create_input_area(self, main_layout: QVBoxLayout):
        """创建输入区域"""
        input_layout = QHBoxLayout()
          # 输入框
        self.input_box = CustomTextEdit(self)
        self.input_box.setPlaceholderText("请输入消息(enter发送，shift+enter换行)")
        self.input_box.setStyleSheet(StyleManager.get_input_style())
        self.input_box.setFixedHeight(80)
        
        # 设置输入框调色板
        self._setup_input_palette()
        
        input_layout.addWidget(self.input_box)

        # 发送按钮
        self.send_button = self._create_send_button()
        input_layout.addWidget(self.send_button)        # 清除历史按钮
        clear_button = self._create_icon_button('icon/clear.svg', 32, self.clear_history)
        clear_button.setFixedSize(50, 50)  # 与发送按钮尺寸一致
        clear_button.setStyleSheet(StyleManager.get_send_button_style())
        input_layout.addWidget(clear_button)

        main_layout.addLayout(input_layout)
    
    def _setup_input_palette(self):
        """设置输入框调色板"""
        palette = self.input_box.palette()
        palette.setColor(self.palette().ColorRole.Base, QColor('#f0f0f0'))
        palette.setColor(self.palette().ColorRole.PlaceholderText, QColor('#999999'))
        palette.setColor(self.palette().ColorRole.Text, QColor('#2d3748'))
        palette.setColor(self.palette().ColorRole.Window, QColor('#f0f0f0'))
        palette.setColor(self.palette().ColorRole.WindowText, QColor('#2d3748'))
        palette.setColor(self.palette().ColorRole.Button, QColor('#f0f0f0'))
        palette.setColor(self.palette().ColorRole.ButtonText, QColor('#2d3748'))
        self.input_box.setPalette(palette)
    def _create_send_button(self) -> QPushButton:
        """创建发送按钮"""
        self.send_button = QPushButton()
        self.send_button.setFixedSize(50, 50)
        
        try:
            self.send_icon = QIcon(resource_path('icon/send.svg'))
            self.stop_icon = QIcon(resource_path('icon/stop.svg'))
              # 创建发送图标
            send_pixmap = QPixmap(32, 32)
            send_pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(send_pixmap)
            svg_renderer = QSvgRenderer(resource_path('icon/send.svg'))
            svg_renderer.render(painter)
            painter.end()
            
            self.send_button.setIcon(QIcon(send_pixmap))
            self.send_button.setIconSize(QSize(32, 32))
        except Exception as e:
            print(f"发送/停止图标加载失败: {e}")
        
        self.send_button.setStyleSheet(StyleManager.get_send_button_style())
        self.send_button.clicked.connect(self.send_message)
        return self.send_button

    def show_api_key_dialog(self):
        """显示API密钥对话框"""
        dialog = APIKeyDialog(self.config_manager, self)
        dialog.exec()
    def show_settings_dialog(self):
        """显示设置对话框"""
        dialog = ModelSelectionDialog(self.config_manager, self)
        if dialog.exec():
            selected_model = dialog.get_selected_model()
            if selected_model:
                print(f"用户选择的模型: {selected_model}")
                # 保存选择的模型
                self.config_manager.save_current_model(selected_model)
                
                # 更新当前状态
                self.current_model = selected_model
                self._update_ui_state()
                
                # 更新模型标签
                self._update_model_label()

    def add_message(self, content: str, align_right: bool = False, message_id: int = None):
        """添加消息到界面"""
        message_widget = MessageWidget(content, align_right, message_id, self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
        # 延迟滚动到底部
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scroll_bar = self.scroll_area.verticalScrollBar()
        target_value = scroll_bar.maximum()
        current_value = scroll_bar.value()
        
        # 创建动画
        self.scroll_animation = QPropertyAnimation(scroll_bar, b"value")
        
        # 动态计算动画时长
        distance = abs(target_value - current_value)
        base_duration = 1200
        duration = min(base_duration, int(base_duration * (1 + math.log10(1 + distance/100))))
        
        self.scroll_animation.setDuration(duration)
        self.scroll_animation.setStartValue(current_value)
        self.scroll_animation.setEndValue(target_value)
        self.scroll_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.scroll_animation.start()

    def send_message(self):
        """发送消息"""
        if self.send_button.property("waiting"):
            self._interrupt_ai_response()
            return

        # 检查API密钥
        api_key = self.config_manager.get_api_key_for_model(self.current_model)
        if not api_key:
            ToastWidget("无API Key", self).show()
            return

        text = self.input_box.toPlainText().strip()
        if not text:
            ToastWidget("消息不能为空！", self).show()
            return
            
        # 保存用户消息到数据库
        message_id = self.db.save_message(text, 'user', self.conversation_id)
        self.add_message(text, align_right=True, message_id=message_id)
          # 设置等待状态
        self._set_waiting_state(True)
        self.get_ai_response(text)
    
    def _interrupt_ai_response(self):
        """中断AI响应"""
        if self.ai_thread and self.ai_thread.isRunning():
            self.ai_thread.terminate()
            self.ai_thread.wait()
            self.timer.stop()
            self._set_waiting_state(False)
            ToastWidget("已中断", self).show()
    
    def _set_waiting_state(self, waiting: bool):
        """设置等待状态"""
        self.input_box.setDisabled(waiting)
        if waiting:
            self.input_box.clear()
            self.timer.start(500)
            self.send_button.setProperty("waiting", True)
            self.send_button.setIcon(self.stop_icon)
        else:
            self.send_button.setProperty("waiting", False)
            self.send_button.setIcon(self.send_icon)
            self.input_box.clear()  # 清空输入框
            self.input_box.setFocus()  # 恢复输入框焦点
            
        self.send_button.setStyleSheet(self.send_button.styleSheet())    
        
    def get_ai_response(self, text: str):
        """获取AI响应（使用流式输出）"""
        api_key = self.config_manager.get_api_key_for_model(self.current_model)
        history_messages = self.db.get_conversation_history(self.conversation_id)

        # 重置流式输出状态
        self.current_ai_message_widget = None
        self.full_ai_response = ""

        # 创建并启动AI流式线程
        self.ai_thread = AIStreamThread(text, api_key, history_messages, self.current_model)
        self.ai_thread.chunk_received.connect(self.handle_ai_chunk)
        self.ai_thread.stream_finished.connect(self.handle_ai_stream_finished)
        self.ai_thread.error_occurred.connect(self.handle_error)
        self.ai_thread.start()
    def handle_ai_chunk(self, chunk: str):
        """处理AI流式响应片段"""
        self.full_ai_response += chunk
        
        if self.current_ai_message_widget is None:
            # 创建新的AI消息组件
            self.current_ai_message_widget = MessageWidget("", align_right=False, parent=self)
            self.message_layout.insertWidget(self.message_layout.count() - 1, self.current_ai_message_widget)
            # 立即滚动到新消息
            QTimer.singleShot(10, self.scroll_to_bottom)
        
        # 更新消息内容
        self.current_ai_message_widget.update_content(self.full_ai_response)
        
        # 确保滚动到底部，但使用更短的延迟
        QTimer.singleShot(20, self.scroll_to_bottom)
    
    def handle_ai_stream_finished(self, full_text: str):
        """处理AI流式响应完成"""
        self.timer.stop()
        self._set_waiting_state(False)
        
        # 清理AI响应文本
        cleaned_text = full_text.strip()
        
        # 保存AI响应到数据库
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, sender, conversation_id) VALUES (?, ?, ?)',
                      (cleaned_text, "ai", self.conversation_id))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # 更新消息组件的message_id
        if self.current_ai_message_widget:
            self.current_ai_message_widget.message_id = message_id
        
        # 重置状态
        self.current_ai_message_widget = None
        self.full_ai_response = ""
    def handle_ai_response(self, text: str):
        """处理AI响应"""
        self.timer.stop()
        self._set_waiting_state(False)
        
        # 清理AI响应文本，去除开头和结尾的空行和空白字符
        cleaned_text = text.strip()
        
        # 保存AI响应（保存原始响应）
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO messages (content, sender, conversation_id) VALUES (?, ?, ?)',
                      (cleaned_text, "ai", self.conversation_id))
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.add_message(cleaned_text, align_right=False, message_id=message_id)

    def handle_error(self, message: str):
        """处理错误"""
        self.timer.stop()
        self._set_waiting_state(False)
        self.add_message(f"错误: {message}", align_right=False)

    def update_dot_animation(self):
        """更新等待动画"""
        self.dot_count = (self.dot_count + 1) % 4
        dots = '.' * self.dot_count
        self.input_box.setPlainText(f"等待ai回复{dots}")

    def copy_message_content(self, content: str):
        """复制消息内容"""
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        ToastWidget("已复制", self).show()

    def delete_message(self, message_widget):
        """删除消息"""
        # 如果消息有ID，从数据库中删除
        if hasattr(message_widget, 'message_id') and message_widget.message_id is not None:
            self.db.delete_message(message_widget.message_id)
        
        # 从UI中移除
        self.message_layout.removeWidget(message_widget)
        message_widget.deleteLater()

    def clear_history(self):
        """清除历史记录"""
        dialog = ConfirmDialog("确定要清除所有聊天记录吗？\n此操作不可恢复。", "确认清除", self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 清除数据库
            if hasattr(self.db, '_conn') and self.db._conn:
                self.db._conn.close()
            
            if os.path.exists(self.db.db_path):
                os.remove(self.db.db_path)
            
            # 重新初始化数据库
            self.db.init_database()
            
            # 清除UI消息
            while self.message_layout.count() > 1:
                item = self.message_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            ToastWidget("已清空", self).show()


def main():
    """主函数"""
    # 启用高DPI缩放支持
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

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


if __name__ == "__main__":
    main()
