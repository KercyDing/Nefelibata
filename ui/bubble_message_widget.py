"""
气泡消息组件 - 使用新的AdvancedTextWidget重新实现MessageWidget
集成thinking功能和流式更新，提供不同的气泡样式
"""
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSizePolicy, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from utils.resources import resource_path
from .styles import StyleManager
from .advanced_text_widget import AdvancedTextWidget


class BubbleMessageWidget(QWidget):
    """使用新AdvancedTextWidget的气泡消息组件"""
    
    def __init__(self, content: str, align_right: bool = False, message_id: int = None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.message_id = message_id
        self.content = content.strip() if content else ""
        self.align_right = align_right
        
        # 新组件引用
        self.message_widget = None  # 主要消息组件
        self.thinking_widget = None  # 思考过程组件
        
        # 流式处理状态变量
        self.is_in_thinking_mode = False
        self.current_thinking_content = ""
        self.current_normal_content = ""
        
        self._setup_ui()
        
    def update_content(self, new_content: str):
        """动态更新消息内容"""
        self.content = new_content.strip() if new_content else ""
        self._process_streaming_content()
        
    def append_content(self, additional_content: str):
        """追加内容到现有消息（流式更新）"""
        self.content += additional_content
        self._process_streaming_content()
        
    def _setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # 为AI消息创建思考过程区域（初始隐藏）
        if not self.align_right:
            self._create_thinking_area(main_layout)
        
        # 创建主消息区域
        self._create_message_area(main_layout)
        
        # 创建按钮区域
        self._create_button_area(main_layout)
        
        # 初始化内容显示
        if self.content:
            if not self.align_right and self._contains_thinking_tags(self.content):
                # 静态加载时解析thinking内容
                self._parse_initial_content()
            else:
                self._update_message_content(self.content)
    def _create_thinking_area(self, main_layout: QVBoxLayout):
        """创建思考过程区域"""
        thinking_container = QWidget()
        thinking_layout = QHBoxLayout(thinking_container)
        thinking_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建思考过程文本组件
        self.thinking_widget = AdvancedTextWidget()
        self.thinking_widget.setBackgroundColor('#f0f8ff')
        self.thinking_widget.setBorderRadius(10)
        self.thinking_widget.setPadding(8)
        self.thinking_widget.setFontSize(12)
        self.thinking_widget.setMaximumWidth(800)   # 调整最大宽度
        self.thinking_widget.setMinimumWidth(300)   # 设置最小宽度
        self.thinking_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # 设置特殊样式
        self.thinking_widget.setStyleSheet("""
            QTextEdit {
                border: 1px dashed #87ceeb;
                color: #4682b4;
                background-color: #f0f8ff;
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        self.thinking_widget.setVisible(False)  # 初始隐藏
        
        thinking_layout.addWidget(self.thinking_widget)
        thinking_layout.addStretch()
        main_layout.addWidget(thinking_container)
    def _create_message_area(self, main_layout: QVBoxLayout):
        """创建主消息区域"""
        message_container = QWidget()
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
          # 创建消息文本组件
        self.message_widget = AdvancedTextWidget()
        self.message_widget.setMaximumWidth(800)  # 调整最大宽度
        self.message_widget.setMinimumWidth(300)   # 设置最小宽度
        self.message_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # 根据消息类型设置样式
        if self.align_right:
            # 用户消息样式
            self.message_widget.setBackgroundColor('#a0e6a0')
            self.message_widget.setBorderRadius(15)
            self.message_widget.setPadding(12)
            self.message_widget.setFontSize(14)
            message_layout.addStretch()
            message_layout.addWidget(self.message_widget)
        else:
            # AI消息样式
            self.message_widget.setBackgroundColor('white')
            self.message_widget.setBorderRadius(15)
            self.message_widget.setPadding(12)
            self.message_widget.setFontSize(14)
            message_layout.addWidget(self.message_widget)
            message_layout.addStretch()
        
        main_layout.addWidget(message_container)
    
    def _create_button_area(self, main_layout: QVBoxLayout):
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
        
        main_layout.addWidget(button_widget)
    
    def _process_streaming_content(self):
        """处理流式内容，实时检测thinking标签"""
        if self.align_right:  # 用户消息不需要处理thinking
            self._update_message_content(self.content)
            return
        
        content = self.content
        
        # 检查是否包含<think>标签
        if '<think>' in content:
            if not self.is_in_thinking_mode:
                # 进入思考模式
                self.is_in_thinking_mode = True
                if self.message_widget:
                    self.message_widget.setVisible(False)
            
            # 提取思考内容
            think_start = content.find('<think>')
            if think_start != -1:
                # 处理<think>之前的正常内容
                before_think = content[:think_start]
                self.current_normal_content = before_think
                
                # 处理思考内容
                think_content_start = think_start + 7  # len('<think>')
                think_end = content.find('</think>', think_content_start)
                
                if think_end != -1:
                    # 找到了完整的</think>标签
                    thinking_content = content[think_content_start:think_end]
                    after_think = content[think_end + 8:]  # len('</think>')
                    
                    # 更新思考内容并完成思考模式
                    self._update_thinking_content(thinking_content, completed=True)
                    
                    # 退出思考模式
                    self.is_in_thinking_mode = False
                    
                    # 显示正常消息
                    if self.message_widget:
                        self.message_widget.setVisible(True)
                    
                    # 合并所有正常内容
                    full_normal_content = (self.current_normal_content + after_think).strip()
                    if full_normal_content:
                        self._update_message_content(full_normal_content)
                    else:
                        self._update_message_content("✨ 思考完成")
                else:
                    # 还没有找到</think>，继续更新思考内容
                    thinking_content = content[think_content_start:]
                    self._update_thinking_content(thinking_content, completed=False)
        else:
            # 没有<think>标签的情况
            if self.is_in_thinking_mode:
                # 如果正在思考模式，这些是思考内容的延续
                full_content = self.content
                think_start = full_content.find('<think>')
                if think_start != -1:
                    think_content_start = think_start + 7
                    current_thinking = full_content[think_content_start:]
                    self._update_thinking_content(current_thinking, completed=False)
            else:
                # 正常内容更新
                if self.message_widget:
                    self.message_widget.setVisible(True)
                self._update_message_content(content)
    
    def _update_thinking_content(self, content: str, completed: bool = False):
        """更新思考过程内容"""
        if not self.thinking_widget:
            return
        
        # 清理内容，确保不显示</think>标签
        clean_content = content.replace('</think>', '').strip()
        
        if completed:
            # 思考完成，显示完整内容
            thinking_text = f"💭 思考过程：\n{clean_content}"
            self.thinking_widget.set_plain_content(thinking_text)
            self.thinking_widget.setVisible(True)
        else:
            # 思考进行中，显示当前内容 + 光标动画
            thinking_text = f"💭 思考中...\n{clean_content}▊"
            self.thinking_widget.set_plain_content(thinking_text)
            self.thinking_widget.setVisible(True)
    
    def _update_message_content(self, content: str):
        """更新正常消息内容"""
        if not self.message_widget or not content:
            return
        
        # 用户消息强制为普通文本，AI消息自动检测格式
        if self.align_right:
            self.message_widget.set_plain_content(content)
        else:
            self.message_widget.set_content(content)
    
    def _parse_initial_content(self):
        """解析初始内容，正确处理thinking标签（用于静态加载）"""
        if '<think>' in self.content and '</think>' in self.content:
            # 提取thinking内容和正常内容
            think_start = self.content.find('<think>')
            think_end = self.content.find('</think>', think_start)
            
            if think_start != -1 and think_end != -1:
                # 分离内容
                before_think = self.content[:think_start]
                thinking_content = self.content[think_start + 7:think_end]
                after_think = self.content[think_end + 8:]
                
                # 显示thinking内容
                if thinking_content.strip():
                    self._update_thinking_content(thinking_content, completed=True)
                
                # 合并并显示正常内容
                normal_content = (before_think + after_think).strip()
                if normal_content:
                    self._update_message_content(normal_content)
                else:
                    self._update_message_content("✨ 思考完成")
            else:
                # thinking标签不完整，按正常内容处理
                self._update_message_content(self.content)
        else:
            # 没有thinking标签，按正常内容处理
            self._update_message_content(self.content)
    
    def _contains_thinking_tags(self, content: str) -> bool:
        """检查内容是否包含thinking标签"""
        return '<think>' in content and '</think>' in content
    
    def _copy_message(self):
        """复制消息内容"""
        if self.parent and hasattr(self.parent, 'copy_message_content'):
            self.parent.copy_message_content(self.content)
    
    def _delete_message(self):
        """删除消息"""
        if self.parent and hasattr(self.parent, 'delete_message'):
            self.parent.delete_message(self)


class ThinkingBubbleWidget(AdvancedTextWidget):
    """专门用于显示思考过程的气泡组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_thinking_style()
    def _setup_thinking_style(self):
        """设置思考气泡样式"""
        self.setBackgroundColor('#f0f8ff')
        self.setBorderRadius(10)
        self.setPadding(8)
        self.setFontSize(12)
        self.setMaximumWidth(800)   # 调整最大宽度
        self.setMinimumWidth(300)   # 设置最小宽度
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # 设置虚线边框样式
        self.setStyleSheet("""
            QTextEdit {
                border: 1px dashed #87ceeb;
                color: #4682b4;
                background-color: #f0f8ff;
                border-radius: 10px;
                padding: 8px;
                font-size: 12px;
            }
        """)
    
    def set_thinking_content(self, content: str, is_complete: bool = False):
        """设置思考内容"""
        if is_complete:
            thinking_text = f"💭 思考过程：\n{content}"
        else:
            thinking_text = f"💭 思考中...\n{content}▊"
        
        self.set_plain_content(thinking_text)
