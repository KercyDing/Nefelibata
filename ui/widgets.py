"""
自定义控件
"""
from PyQt6.QtWidgets import QTextEdit, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QDialog
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QFontMetrics, QTextDocument
from PyQt6 import QtGui
from utils.resources import resource_path
from .styles import StyleManager
import re
import markdown


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


class MarkdownTextWidget(QTextEdit):
    """支持Markdown渲染的文本显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(0)  # 无边框
        self.setContentsMargins(0, 0, 0, 0)
        
        # 设置基本样式
        self.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # 连接文档大小变化信号，自动调整高度
        self.document().contentsChanged.connect(self._adjust_height)
        
    def set_markdown_content(self, markdown_text: str, background_color: str = "white", 
                           border_radius: int = 15, padding: int = 12, font_size: int = 14):
        """设置Markdown内容并应用样式"""
        if not markdown_text:
            markdown_text = ""
            
        # 将Markdown转换为HTML
        html_content = markdown.markdown(markdown_text, extensions=['nl2br', 'codehilite', 'tables'])
        
        # 添加CSS样式
        styled_html = f"""
        <div style="
            background-color: {background_color};
            border-radius: {border_radius}px;
            padding: {padding}px;
            font-size: {font_size}px;
            line-height: 1.4;
            color: #333;
            margin: 0;
            width: 100%;
            box-sizing: border-box;
        ">
            {html_content}
        </div>
        """
        
        self.setHtml(styled_html)
        # 立即调整高度，然后延迟再次调整以确保渲染完成
        QTimer.singleShot(10, self._adjust_height)
        QTimer.singleShot(50, self._adjust_height)
        
    def _adjust_height(self):
        """根据内容自动调整高度"""
        # 确保文档有内容
        if not self.document():
            return
            
        # 设置文档宽度以正确计算高度
        self.document().setTextWidth(self.width() if self.width() > 0 else 960)
        
        # 获取文档高度
        doc_height = self.document().size().height()
        
        # 添加一些缓冲空间
        final_height = max(int(doc_height) + 10, 30)  # 最小高度30px
        
        # 设置固定高度
        self.setFixedHeight(final_height)
        self.setMaximumHeight(final_height)
        self.setMinimumHeight(final_height)
        
    def resizeEvent(self, event):
        """窗口大小改变时重新调整高度"""
        super().resizeEvent(event)
        # 延迟调整高度，确保宽度设置生效
        QTimer.singleShot(1, self._adjust_height)
        
    def sizeHint(self):
        """返回建议大小"""
        if not self.document():
            return QSize(960, 30)
            
        doc_size = self.document().size()
        width = min(int(doc_size.width()), 960)
        height = max(int(doc_size.height()) + 10, 30)
        return QSize(width, height)


class MessageWidget(QWidget):
    """消息组件"""    
    def __init__(self, content: str, align_right: bool = False, message_id: int = None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.message_id = message_id
        # 清理消息内容，去除开头和结尾的空行和空白字符
        self.content = content.strip() if content else ""
        self.align_right = align_right
        self.message_widget = None  # 存储消息组件引用以便动态更新（可能是QLabel或MarkdownTextWidget）
        self.thinking_widget = None  # 存储思考过程组件引用
        
        # 流式处理状态变量
        self.is_in_thinking_mode = False  # 是否正在思考模式
        self.current_thinking_content = ""  # 当前思考内容缓存
        self.current_normal_content = ""  # 当前正常内容缓存
        self.content_buffer = ""  # 内容缓冲区
        
        self._setup_ui()
        
    def update_content(self, new_content: str):
        """动态更新消息内容"""
        self.content = new_content.strip() if new_content else ""
        self._process_streaming_content()
        # 强制更新布局和重绘
        self._force_layout_update()
    def append_content(self, additional_content: str):
        """追加内容到现有消息（流式更新）"""
        self.content += additional_content
        self._process_streaming_content()
        # 强制更新布局和重绘
        self._force_layout_update()
        
    def _process_streaming_content(self):
        """处理流式内容，实时检测thinking标签"""
        if self.align_right:  # 用户消息不需要处理thinking
            self._update_normal_content(self.content)
            return
            
        # 处理AI消息的流式内容
        content = self.content
        
        # 检查是否包含<think>标签
        if '<think>' in content:
            if not self.is_in_thinking_mode:
                # 进入思考模式
                self.is_in_thinking_mode = True
                # 隐藏正常消息框
                if self.message_widget:
                    self.message_widget.setVisible(False)
            
            # 提取思考内容
            think_start = content.find('<think>')
            if think_start != -1:
                # 处理<think>之前的正常内容
                before_think = content[:think_start]
                self.current_normal_content = before_think  # 缓存正常内容
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
                    
                    # 显示正常消息框
                    if self.message_widget:
                        self.message_widget.setVisible(True)
                    
                    # 合并所有正常内容并清理空白行
                    full_normal_content = (self.current_normal_content + after_think).strip()
                    if full_normal_content:
                        self._update_normal_content(full_normal_content)
                    else:
                        # 如果没有正常内容，显示默认消息
                        self._update_normal_content("✨ 思考完成")
                else:
                    # 还没有找到</think>，继续更新思考内容
                    thinking_content = content[think_content_start:]
                    self._update_thinking_content(thinking_content, completed=False)
        else:
            # 没有<think>标签的情况
            if self.is_in_thinking_mode:
                # 如果正在思考模式，这些是思考内容的延续
                # 从上次的<think>位置开始获取思考内容
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
                self._update_normal_content(content)

    def _create_thinking_widget(self):
        """动态创建思考过程组件"""
        if self.thinking_widget or self.align_right:
            return
            
        # 在现有布局中插入thinking widget
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            # 创建思考过程区域
            thinking_widget = QWidget()
            thinking_layout = QHBoxLayout(thinking_widget)
            thinking_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建思考过程标签
            self.thinking_widget = QLabel()
            self.thinking_widget.setWordWrap(True)            
            self.thinking_widget.setStyleSheet("""
                QLabel {
                    background-color: #f0f8ff;
                    border: 1px dashed #87ceeb;
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 12px;
                    color: #4682b4;
                    max-width: 960px;
                }
            """)
            self.thinking_widget.setVisible(False)
            
            thinking_layout.addWidget(self.thinking_widget)
            thinking_layout.addStretch()
            # 插入到消息内容之前
            main_layout.insertWidget(0, thinking_widget)

    def _update_thinking_content(self, content: str, completed: bool = False):
        """更新思考过程内容"""
        if not self.thinking_widget:
            return
            
        # 清理内容，确保不显示</think>标签
        clean_content = content.replace('</think>', '').strip()
        
        if completed:
            # 思考完成，显示完整内容（保持可见，不自动隐藏）
            self.thinking_widget.setText(f"💭 思考过程：\n{clean_content}")
            self.thinking_widget.setVisible(True)
        else:
            # 思考进行中，显示当前内容 + 光标动画
            self.thinking_widget.setText(f"💭 思考中...\n{clean_content}▊")
            self.thinking_widget.setVisible(True)
    
    def _update_normal_content(self, content: str):
        """更新正常消息内容"""
        if not self.message_widget:
            return
            
        # 清理内容，去除开头和结尾的空白行
        cleaned_content = content.strip()
        
        if cleaned_content:
            self._format_message_text(cleaned_content)
            # 确保正常消息可见（特别是在思考模式结束后）
            self.message_widget.setVisible(True)
        else:
            # 如果没有正常内容，显示默认提示
            if not self.is_in_thinking_mode:
                self._format_message_text("✨ AI正在回复...")
                self.message_widget.setVisible(True)
            else:
                # 如果在思考模式且没有正常内容，隐藏正常消息
                self.message_widget.setVisible(False)    
                
    def _parse_initial_content(self):
        """解析初始内容，正确处理thinking标签（用于静态加载）"""
        if self.align_right or not self.content:
            # 用户消息或空内容直接显示
            self._format_message_text(self.content)
            return
            
        # AI消息，检查是否包含thinking内容
        if '<think>' in self.content and '</think>' in self.content:
            # 提取thinking内容和正常内容
            think_start = self.content.find('<think>')
            think_end = self.content.find('</think>', think_start)
            
            if think_start != -1 and think_end != -1:
                # 分离内容
                before_think = self.content[:think_start]
                thinking_content = self.content[think_start + 7:think_end]  # 7 = len('<think>')
                after_think = self.content[think_end + 8:]  # 8 = len('</think>')
                
                # 显示thinking内容
                if thinking_content.strip():
                    self._update_thinking_content(thinking_content, completed=True)
                
                # 合并并显示正常内容
                normal_content = (before_think + after_think).strip()
                if normal_content:
                    self._format_message_text(normal_content)
                else:
                    # 如果没有正常内容，显示默认消息
                    self._format_message_text("✨ 思考完成")
            else:
                # thinking标签不完整，按正常内容处理
                self._format_message_text(self.content)
        else:
            # 没有thinking标签，按正常内容处理
            self._format_message_text(self.content)

    def _parse_content(self):
        """解析消息内容，分离思考过程和实际回复（兼容旧版本）"""
        # 使用正则表达式查找<think>...</think>内容
        think_pattern = r'<think>(.*?)</think>'
        think_matches = re.findall(think_pattern, self.content, re.DOTALL)
        
        # 移除<think>...</think>标签，保留实际回复内容
        actual_content = re.sub(think_pattern, '', self.content, flags=re.DOTALL).strip()
        
        return think_matches, actual_content
    
    def _update_display_content(self):
        """更新显示内容（兼容旧版本，重定向到新的流式处理）"""
        self._process_streaming_content()
              
    def _format_message_text(self, content: str = None):
        """格式化消息文本，智能选择QLabel或MarkdownTextWidget"""
        if content is None:
            _, content = self._parse_content()
        
        if not content:
            content = ""
            
        # 检测是否包含Markdown格式
        has_markdown = self._detect_markdown(content)
        
        # 获取背景颜色
        background_color = '#a0e6a0' if self.align_right else 'white'
        
        if has_markdown and not self.align_right:
            # 使用MarkdownTextWidget渲染Markdown内容
            if not isinstance(self.message_widget, MarkdownTextWidget):
                # 需要替换现有的QLabel
                self._replace_message_widget_with_markdown()
            
            self.message_widget.set_markdown_content(
                content, 
                background_color=background_color,
                border_radius=15,
                padding=12,
                font_size=14
            )
        else:
            # 使用QLabel显示普通文本
            if not isinstance(self.message_widget, QLabel):
                # 需要替换现有的MarkdownTextWidget
                self._replace_message_widget_with_label()
            
            self._format_plain_text(content, background_color)
    
    def _detect_markdown(self, text: str) -> bool:
        """检测文本是否包含Markdown格式"""
        if not text:
            return False
            
        # 检测常见的Markdown模式
        markdown_patterns = [
            r'\*\*.*?\*\*',      # 粗体
            r'\*.*?\*',          # 斜体
            r'`.*?`',            # 内联代码
            r'```[\s\S]*?```',   # 代码块
            r'^#{1,6}\s',        # 标题
            r'^\* ',             # 无序列表
            r'^\d+\. ',          # 有序列表
            r'\[.*?\]\(.*?\)',   # 链接
            r'^\|.*\|.*$',       # 表格
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
    def _replace_message_widget_with_markdown(self):
        """将QLabel替换为MarkdownTextWidget"""
        if isinstance(self.message_widget, MarkdownTextWidget):
            return
            
        # 找到消息widget的父布局
        parent_layout = None
        widget_index = -1
        
        if self.message_widget and self.message_widget.parent():
            parent = self.message_widget.parent()
            if hasattr(parent, 'layout') and parent.layout():
                parent_layout = parent.layout()
                for i in range(parent_layout.count()):
                    item = parent_layout.itemAt(i)
                    if item and item.widget() == self.message_widget:
                        widget_index = i
                        break
        
        # 移除旧的widget
        if self.message_widget:
            self.message_widget.setParent(None)
            self.message_widget.deleteLater()
        
        # 创建新的MarkdownTextWidget
        self.message_widget = MarkdownTextWidget()
        self.message_widget.setMaximumWidth(960)
        self.message_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        
        # 将新widget添加到布局中
        if parent_layout and widget_index >= 0:
            parent_layout.insertWidget(widget_index, self.message_widget)
        
        # 强制更新布局
        QTimer.singleShot(1, self._force_layout_update)
    
    def _replace_message_widget_with_label(self):
        """将MarkdownTextWidget替换为QLabel"""
        if isinstance(self.message_widget, QLabel):
            return
            
        # 找到消息widget的父布局
        parent_layout = None
        widget_index = -1
        
        if self.message_widget and self.message_widget.parent():
            parent = self.message_widget.parent()
            if hasattr(parent, 'layout') and parent.layout():
                parent_layout = parent.layout()
                for i in range(parent_layout.count()):
                    item = parent_layout.itemAt(i)
                    if item and item.widget() == self.message_widget:
                        widget_index = i
                        break
        
        # 移除旧的widget
        if self.message_widget:
            self.message_widget.setParent(None)
            self.message_widget.deleteLater()
        
        # 创建新的QLabel
        self.message_widget = QLabel()
        self.message_widget.setWordWrap(True)
        
        # 将新widget添加到布局中
        if parent_layout and widget_index >= 0:
            parent_layout.insertWidget(widget_index, self.message_widget)
        
        # 强制更新布局
        QTimer.singleShot(1, self._force_layout_update)
    
    def _format_plain_text(self, content: str, background_color: str):
        """使用QLabel格式化普通文本"""
        font_metrics = QFontMetrics(self.message_widget.font())
        max_width = 960
        
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
        formatted_text = '\n'.join(formatted_lines)
        self.message_widget.setText(formatted_text)
        
        # 动态计算气泡框的合适宽度
        text_width = max(font_metrics.horizontalAdvance(line) for line in formatted_lines) if formatted_lines else 100
        bubble_width = min(max_width, text_width + 24)  # 加上内边距
        
        # 设置大小策略和约束
        self.message_widget.setMaximumWidth(max_width)
        self.message_widget.setMinimumWidth(min(bubble_width, max_width))
        self.message_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.message_widget.setStyleSheet(f"""
            QLabel {{
                background-color: {background_color};
                border-radius: 15px;
                padding: 12px;
                font-size: 14px;
                max-width: {max_width}px;
            }}
        """)

    def _force_layout_update(self):
        """强制布局更新"""
        # 更新标签大小
        if self.message_widget:
            self.message_widget.adjustSize()
            self.message_widget.updateGeometry()
        
        if self.thinking_widget:
            self.thinking_widget.adjustSize()
            self.thinking_widget.updateGeometry()
        
        # 更新组件大小
        self.adjustSize()
        self.updateGeometry()
        
        # 通知父布局更新
        if self.parent:
            self.parent.updateGeometry()
            
        # 强制重绘
        self.repaint()
        
        # 使用定时器确保布局完全更新
        QTimer.singleShot(1, self._delayed_layout_update)

    def _delayed_layout_update(self):
        """延迟布局更新"""
        if self.parent and hasattr(self.parent, 'message_layout'):
            # 触发父布局的重新计算
            self.parent.message_layout.invalidate()
            self.parent.message_layout.activate()

    def _setup_ui(self):
        """设置UI"""
        message_layout = QVBoxLayout(self)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(5)
          # 为AI消息预创建思考过程区域（初始隐藏）
        if not self.align_right:
            thinking_widget_container = QWidget()
            thinking_layout = QHBoxLayout(thinking_widget_container)
            thinking_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建思考过程标签
            self.thinking_widget = QLabel()
            self.thinking_widget.setWordWrap(True)            # 设置与正常消息框相同的最大宽度和约束
            self.thinking_widget.setMaximumWidth(960)
            self.thinking_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
            self.thinking_widget.setStyleSheet("""
                QLabel {
                    background-color: #f0f8ff;
                    border: 1px dashed #87ceeb;
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 12px;
                    color: #4682b4;
                }
            """)
            self.thinking_widget.setVisible(False)  # 初始隐藏
            
            thinking_layout.addWidget(self.thinking_widget)
            thinking_layout.addStretch()
            message_layout.addWidget(thinking_widget_container)
        
        # 创建消息内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建消息组件（初始为QLabel，根据内容自动切换）
        self.message_widget = QLabel()
        self.message_widget.setWordWrap(True)
          # 初始化显示内容
        display_content = self.content if self.content else ("正在思考..." if not self.align_right else "")
        if display_content:
            # 静态加载时解析thinking内容
            self._parse_initial_content()
        else:
            self._format_message_text(display_content)
        
        # 根据发送者调整消息位置
        if self.align_right:
            content_layout.addStretch()
        content_layout.addWidget(self.message_widget)
        if not self.align_right:
            content_layout.addStretch()
        
        message_layout.addWidget(content_widget)
        
        # 创建按钮区域
        self._create_button_area(message_layout)

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
