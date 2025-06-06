"""
高级文本显示组件
支持Markdown渲染、自动换行、高度自适应等功能
完全替代QLabel，提供更强大的功能
"""

import re
import uuid
import markdown # type: ignore

from PyQt6.QtWidgets import QTextEdit, QApplication
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QDesktopServices, QWheelEvent, QKeyEvent # MODIFIED
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize, QTimer


class AdvancedTextWidget(QTextEdit):
    """
    高级文本显示组件
    
    功能特性：
    1. 自动检测并渲染Markdown格式
    2. 支持普通文本显示（类似QLabel）
    3. 自动高度调整
    4. 自动换行
    5. 气泡样式支持
    6. 无滚动条，类似QLabel的表现
    7. 支持选择文本但不可编辑
    """
    
    # 信号
    heightChanged = pyqtSignal(int)  # 高度改变信号
    contentChanged = pyqtSignal()    # 内容改变信号
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 首先初始化属性
        self._content = ""
        self._is_markdown = False
        self._background_color = "white"
        self._border_radius = 15
        self._padding = 12
        self._font_size = 14
        self._max_width = 960
        self._min_height = 30
        self._word_wrap = True
        
        # 基本设置
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(0)  # 无边框
        self.setContentsMargins(0, 0, 0, 0)
          # 连接信号
        self.document().contentsChanged.connect(self._on_content_changed)
        self.document().documentLayoutChanged.connect(self._adjust_height)
        
        # 初始化文档设置
        self._setup_document()
        
        # 更新初始样式
        self._update_widget_style()
    
    def _update_widget_style(self):
        """更新QTextEdit的样式"""
        self.setStyleSheet(f"""
            QTextEdit {{
                border: none;
                background-color: {self._background_color};
                border-radius: {self._border_radius}px;
                padding: {self._padding}px;
                margin: 0px;
                selection-background-color: #3875d7;
                selection-color: white;
            }}
        """)
    
    def _setup_document(self):
        """设置文档属性"""
        doc = self.document()
        doc.setDocumentMargin(0)
        doc.setIndentWidth(20)  # 设置缩进宽度
        
        # 设置默认字体
        font = QFont()
        font.setPointSize(self._font_size)
        doc.setDefaultFont(font)
    
    def set_content(self, content: str, background_color: str = None, 
                   border_radius: int = None, padding: int = None, 
                   font_size: int = None, max_width: int = None):
        """
        设置内容
        
        Args:
            content: 文本内容
            background_color: 背景颜色
            border_radius: 圆角半径
            padding: 内边距
            font_size: 字体大小
            max_width: 最大宽度
        """
        if content is None:
            content = ""
            
        # 更新样式参数
        if background_color is not None:
            self._background_color = background_color
        if border_radius is not None:
            self._border_radius = border_radius
        if padding is not None:
            self._padding = padding
        if font_size is not None:
            self._font_size = font_size
        if max_width is not None:
            self._max_width = max_width
            
        # 保存原始内容
        self._content = content
        
        # 检测是否为Markdown
        self._is_markdown = self._detect_markdown(content)
        
        # 根据内容类型渲染
        if self._is_markdown:
            self._render_markdown_content(content)
        else:
            self._render_plain_content(content)
        
        # 发出内容改变信号
        self.contentChanged.emit()
    
    def set_markdown_content(self, markdown_text: str, **kwargs):
        """强制设置为Markdown内容"""
        self._is_markdown = True
        self.set_content(markdown_text, **kwargs)
    
    def set_plain_content(self, plain_text: str, **kwargs):
        """强制设置为普通文本内容"""
        self._is_markdown = False
        self.set_content(plain_text, **kwargs)
    
    def _detect_markdown(self, text: str) -> bool:
        """检测文本是否包含Markdown格式"""
        if not text or not isinstance(text, str):
            return False
            
        # 检测常见的Markdown模式
        markdown_patterns = [
            r'\*\*.*?\*\*',          # 粗体
            r'(?<!\*)\*(?!\*).*?(?<!\*)\*(?!\*)',  # 斜体（不与粗体冲突）
            r'`[^`]+`',              # 内联代码
            r'```[\s\S]*?```',       # 代码块
            r'^#{1,6}\s+.+$',        # 标题
            r'^\s*[-*+]\s+',         # 无序列表
            r'^\s*\d+\.\s+',         # 有序列表
            r'\[([^\]]+)\]\(([^)]+)\)',  # 链接
            r'^\s*\|.*\|.*$',        # 表格行
            r'^---+$',               # 水平分割线
            r'>\s+',                 # 引用
            r'!\[([^\]]*)\]\(([^)]+)\)',  # 图片
        ]
        
        for pattern in markdown_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False    
        
    def _render_markdown_content(self, markdown_text: str):
        """渲染Markdown内容"""
        try:
            # 配置markdown扩展
            extensions = [
                'markdown.extensions.nl2br',          # 换行转<br>
                'markdown.extensions.tables',         # 表格支持
                'markdown.extensions.codehilite',     # 代码高亮
                'markdown.extensions.fenced_code',    # 围栏代码块
                'markdown.extensions.toc',           # 目录
                'markdown.extensions.attr_list',     # 属性列表
            ]
            
            # 转换Markdown为HTML
            html_content = markdown.markdown(
                markdown_text, 
                extensions=extensions,
                extension_configs={
                    'markdown.extensions.codehilite': {
                        'css_class': 'highlight',
                        'use_pygments': False,  # 不使用Pygments，使用简单高亮
                    },
                    'markdown.extensions.tables': {},  # 确保表格扩展正确加载
                }
            )
            
            # 后处理HTML：清理代码块中的多余元素
            html_content = self._post_process_code_blocks(html_content)
            
            # 创建完整的HTML文档
            full_html = self._create_styled_html(html_content, is_markdown=True)
            
            # 设置HTML内容
            self.setHtml(full_html)
            self.moveCursor(QTextCursor.MoveOperation.Start) # 新增：确保内容置顶
            
        except Exception as e:
            print(f"Markdown渲染失败: {e}")
            # 渲染失败时回退到普通文本
            self._render_plain_content(markdown_text)
    def _post_process_code_blocks(self, html_content: str) -> str:
        """
        后处理代码块HTML，确保统一的背景并添加复制按钮
        """
        import re
        
        # 匹配代码块并添加复制按钮
        def clean_code_block(match):
            pre_content = match.group(1)
            
            # 移除所有HTML标签，保留纯文本
            import re
            clean_content = re.sub(r'<[^>]+>', '', pre_content)
            
            # 转义HTML特殊字符
            clean_content = (clean_content
                           .replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;'))
            
            # 生成唯一ID用于复制按钮
            import uuid
            code_id = f"code_{uuid.uuid4().hex[:8]}"
            
            # 返回带复制按钮的代码块
            return f'''<div class="code-container">
                <pre id="{code_id}"><code>{clean_content}</code></pre>
                <button class="code-copy-btn" onclick="copyCode('{code_id}')">复制</button>
            </div>'''
        
        # 处理所有代码块
        html_content = re.sub(r'<pre[^>]*>(.*?)</pre>', clean_code_block, html_content, flags=re.DOTALL)
        
        return html_content
    
    def _render_plain_content(self, plain_text: str):
        """渲染普通文本内容"""
        # 处理换行和特殊字符
        escaped_text = (plain_text
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;')
                       .replace('\\n', '<br>'))
        
        # 创建HTML文档
        full_html = self._create_styled_html(escaped_text, is_markdown=False)
        
        # 设置HTML内容
        self.setHtml(full_html)
        self.moveCursor(QTextCursor.MoveOperation.Start) # 新增：确保内容置顶
    
    def _create_styled_html(self, content: str, is_markdown: bool = False) -> str:
        """创建带样式的HTML文档"""          # 基础CSS样式
        base_styles = f"""            body {{
                margin: 0;
                padding: 2px 0 0 0; /* MODIFIED: Added 2px top padding to move text down */
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                font-size: {self._font_size}px;
                line-height: 1.3;
                color: #333;
                background-color: transparent;
                word-wrap: break-word;
                overflow-wrap: break-word;
                max-width: 100%;
                box-sizing: border-box;
                display: block;
            }}
            
            * {{
                max-width: 100%;
                box-sizing: border-box;
            }}
            
            /* 优化段落间距，减少空白行 */
            p {{
                margin: 0;
                padding: 0;
                display: block;
            }}
            
            /* 只有多个段落时才添加间距 */
            p + p {{
                margin-top: 0.8em;
            }}
            
            /* 如果内容只有一个段落，确保没有额外间距 */
            body > p:only-child {{
                margin: 0;
            }}
            
            /* 确保第一个和最后一个元素没有额外的边距 */
            body > *:first-child {{
                margin-top: 0;
            }}
            
            body > *:last-child {{
                margin-bottom: 0;
            }}
        """
        
        # Markdown特有样式
        if is_markdown:
            markdown_styles = """
            h1, h2, h3, h4, h5, h6 {
                margin: 0.5em 0;
                font-weight: bold;
                line-height: 1.2;
            }
            
            h1 { font-size: 1.5em; }
            h2 { font-size: 1.3em; }
            h3 { font-size: 1.1em; }
            h4, h5, h6 { font-size: 1em; }
            
            strong, b {
                font-weight: bold;
            }
            
            em, i {
                font-style: italic;
            }
              code {
                background-color: #f1f3f4;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
            }            /* 代码块样式 - 完全统一的灰色背景，无任何空白间隙 */
            pre {
                position: relative !important;
                background: #f8f9fa !important;
                background-color: #f8f9fa !important;
                background-image: none !important;
                border: 1px solid #e1e4e8 !important;
                border-radius: 6px !important;
                padding: 12px 35px 12px 12px !important;  /* 减少右侧padding从45px到35px */
                margin: 10px 0 !important;
                overflow-x: auto !important;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
                font-size: 0.9em !important;
                line-height: 1.0 !important;  /* 最小行间距 */
                white-space: pre !important;
                word-wrap: normal !important;
                display: block !important;
                width: 100% !important;
                box-sizing: border-box !important;
                min-height: 20px !important;
            }
            
            /* 绝对强制：所有代码块内的元素都使用相同背景 */
            pre,
            pre *,
            pre::before,
            pre::after,
            pre *::before,
            pre *::after {
                background: #f8f9fa !important;
                background-color: #f8f9fa !important;
                background-image: none !important;
                background-attachment: scroll !important;
                background-repeat: no-repeat !important;
                background-position: 0 0 !important;
                background-size: auto !important;
                background-clip: border-box !important;
                background-origin: padding-box !important;
                margin: 0 !important;
                margin-top: 0 !important;
                margin-bottom: 0 !important;
                margin-left: 0 !important;
                margin-right: 0 !important;
                padding: 0 !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                padding-left: 0 !important;
                padding-right: 0 !important;
                border: none !important;
                border-top: none !important;
                border-bottom: none !important;
                border-left: none !important;
                border-right: none !important;
                outline: none !important;
                box-shadow: none !important;
                text-shadow: none !important;
                line-height: 1.0 !important;
                vertical-align: baseline !important;
            }
              /* 代码块容器本身的样式（覆盖上面的通用规则） */
            pre {
                padding: 12px 35px 12px 12px !important;  /* 减少右侧padding */
                margin: 10px 0 !important;
                border: 1px solid #e1e4e8 !important;
                border-radius: 6px !important;
                line-height: 1.0 !important;
            }
            
            /* 代码内容样式 */
            pre code {
                display: block !important;
                width: 100% !important;
                color: #24292e !important;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
                font-size: inherit !important;
                line-height: 1.0 !important;
                white-space: pre !important;
                word-wrap: normal !important;
                overflow: visible !important;
                text-align: left !important;
                text-indent: 0 !important;
            }
            
            /* 处理所有可能的子元素 */
            pre code *,
            pre .highlight *,
            pre .codehilite *,
            pre span,
            pre div,
            pre p {
                display: inline !important;
                white-space: pre !important;
                line-height: 1.0 !important;
                vertical-align: baseline !important;
                text-indent: 0 !important;
            }
            
            /* 完全移除换行产生的间隙 */
            pre br,
            pre code br {
                display: none !important;
                line-height: 0 !important;
                height: 0 !important;
                width: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                content: '' !important;
            }
            
            /* 确保文本节点也不产生额外空白 */
            pre text {
                line-height: 1.0 !important;
                vertical-align: baseline !important;
            }
            
            /* 代码块复制按钮样式 */
            .code-copy-btn {
                position: absolute;
                top: 8px;
                right: 8px;
                background: #ffffff;
                border: 1px solid #d0d7de;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                color: #656d76;
                cursor: pointer;
                opacity: 0.8;
                transition: all 0.2s ease;
                min-width: 50px;
                text-align: center;
            }
            
            .code-copy-btn:hover {
                background: #f3f4f6;
                border-color: #8c959f;
                opacity: 1;
            }
            
            .code-copy-btn:active {
                background: #e9ecef;
                transform: translateY(1px);
            }
            
            ul, ol {
                margin: 0.5em 0;
                padding-left: 2em;
            }
            
            li {
                margin: 0.3em 0;
            }
            
            blockquote {
                border-left: 4px solid #dfe2e5;
                margin: 0.5em 0;
                padding: 0 1em;
                color: #6a737d;
                font-style: italic;
            }
              table {
                border-collapse: collapse;
                margin: 0.8em 0;
                width: 100%;
                border: 1px solid #dfe2e5;
                border-radius: 6px;
                overflow: hidden;
                font-size: 0.95em;
            }
            
            th, td {
                border: 1px solid #dfe2e5;
                padding: 8px 12px;
                text-align: left;
                vertical-align: top;
            }
            
            th {
                background-color: #f6f8fa;
                font-weight: bold;
                border-bottom: 2px solid #dfe2e5;
            }
            
            /* 表格行间隔色彩 */
            tbody tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            tbody tr:hover {
                background-color: #f1f3f4;
            }            a {
                color: #0366d6;
                text-decoration: underline;
                text-underline-offset: 2px;
                border-radius: 3px;
                padding: 1px 2px;
                transition: all 0.2s ease;
                cursor: pointer;
            }
            
            a:hover {
                color: #0073e6;
                text-decoration: underline;
                text-decoration-color: #0073e6;
                background-color: rgba(3, 102, 214, 0.1);
                cursor: pointer;
            }
            
            a:active {
                color: #005cc5;
                background-color: rgba(3, 102, 214, 0.2);
                cursor: pointer;
            }
            
            hr {
                border: none;
                border-top: 1px solid #e1e4e8;
                margin: 1em 0;
            }
            
            img {
                max-width: 100%;
                height: auto;
            }
            """
            base_styles += markdown_styles
        
        # 构建完整HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                {base_styles}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        return html
    def _on_content_changed(self):
        """文档内容改变时的处理"""
        QTimer.singleShot(1, self._adjust_height)    
        
    def _adjust_height(self):
        """根据内容自动调整高度和宽度"""
        if not self.document():
            return
        
        # 首先计算理想宽度
        ideal_width = self._calculate_ideal_width()
        
        # 设置文档宽度
        self.document().setTextWidth(ideal_width)
        
        # 获取文档的理想高度
        doc_height = self.document().size().height()
          # 计算最终高度（调整边距和增加顶部padding补偿）
        content_margins = self.contentsMargins()
        vertical_margins = content_margins.top() + content_margins.bottom() # This is 0 due to setContentsMargins(0,0,0,0)
        # 修正高度计算逻辑，以包含QTextEdit的padding并补偿body的padding-top
        # self._padding 是QTextEdit的内边距 (e.g., 12px)
        # body的padding-top是2px (from _create_styled_html)
        # doc_height includes the body's 2px padding-top.
        # Total height should be doc_height (content) + 2 * self._padding (widget padding).
        # To keep overall height consistent as if body_padding_top was 0, subtract the 2px.
        final_height = max(int(doc_height) + 2 * self._padding - 2, self._min_height)
        
        # 设置固定尺寸
        if self.width() != ideal_width or self.height() != final_height:
            self.setFixedSize(ideal_width, final_height)
            self.heightChanged.emit(final_height)
            
    def _calculate_ideal_width(self) -> int:
        """计算理想宽度 - 智能适应文本长度"""
        if not self._content:
            return 80  # 空内容时的最小宽度
          # 保存当前文档宽度
        original_width = self.document().textWidth()
        try:
            # 设置一个很大的宽度来测量内容的自然宽度（不换行）
            self.document().setTextWidth(9999)
            
            # 强制重新布局 - 使用正确的Qt方法
            self.document().documentLayout().documentSizeChanged.emit(self.document().size())
              # 获取内容的自然宽度
            natural_width = int(self.document().idealWidth())
            
            # 计算最小边距（减少右侧间距）
            min_padding = self._padding * 2 + 5  # 左右padding + 减少的边距
            
            # 计算理想宽度
            content_width = natural_width + min_padding
            
            if content_width <= self._max_width:
                # 短文本：使用契合内容的宽度，最小60px
                ideal_width = max(content_width, 60)
            else:
                # 长文本：使用最大宽度
                ideal_width = self._max_width
            
            return ideal_width
            
        except Exception as e:
            print(f"计算理想宽度时出错: {e}")
            return self._max_width
        finally:
            # 恢复原始宽度
            if original_width > 0:
                self.document().setTextWidth(original_width)
        
    def resizeEvent(self, event):
        """处理窗口大小改变事件"""
        super().resizeEvent(event)
        # 延迟调整高度和宽度，确保设置生效
        QTimer.singleShot(10, self._adjust_height)

    def wheelEvent(self, event: QWheelEvent):
        """
        处理鼠标滚轮事件，忽略它以便父组件可以处理滚动。
        """
        event.ignore() # MODIFIED: Changed from accept() to ignore()
    
    def keyPressEvent(self, event: QKeyEvent):
        """
        处理按键事件，阻止滚动键
        """
        scroll_keys = [
            Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
            Qt.Key.Key_Home, Qt.Key.Key_End
        ]
        if event.key() in scroll_keys:
            event.accept()
            return 

        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """处理鼠标点击事件，实现链接点击功能"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 获取点击位置的文档位置
            cursor = self.cursorForPosition(event.pos())
            
            # 检查是否点击了链接
            link_url = cursor.charFormat().anchorHref()
            if link_url:
                # 打开链接
                self._open_link(link_url)
                return
        
        # 如果不是链接点击，继续默认处理
        super().mousePressEvent(event)
    
    def _open_link(self, url: str):
        """打开链接"""
        try:
            # 确保URL格式正确
            if not url.startswith(('http://', 'https://', 'file://', 'ftp://')):
                if url.startswith('www.'):
                    url = 'https://' + url
                elif '.' in url:  # 简单的域名检测
                    url = 'https://' + url
                else:
                    print(f"无效的URL格式: {url}")
                    return
            
            # 使用系统默认浏览器打开链接
            success = QDesktopServices.openUrl(QUrl(url))
            if not success:
                print(f"无法打开链接: {url}")
        except Exception as e:
            print(f"打开链接时出错: {e}")
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现链接hover效果"""
        cursor = self.cursorForPosition(event.pos())
        link_url = cursor.charFormat().anchorHref()
        
        if link_url:
            # 在链接上时显示手型光标
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            # 不在链接上时恢复默认光标
            self.setCursor(Qt.CursorShape.IBeamCursor)
        
        super().mouseMoveEvent(event)    
        
    def sizeHint(self):
        """返回建议大小"""
        if not self.document():
            return QSize(300, self._min_height)
        
        # 使用相同的宽度计算逻辑
        ideal_width = self._calculate_ideal_width()
        
        # 设置文档宽度并计算高度
        self.document().setTextWidth(ideal_width)
        doc_size = self.document().size()
        height = max(int(doc_size.height()) + 10, self._min_height)
        
        return QSize(ideal_width, height)
    def minimumSizeHint(self):
        """返回最小大小提示"""
        return QSize(60, self._min_height)  # 支持非常小的宽度
    
    # QLabel兼容方法
    def setText(self, text: str):
        """兼容QLabel的setText方法"""
        self.set_content(text)
    
    def text(self) -> str:
        """兼容QLabel的text方法，返回原始文本内容"""
        return self._content
    
    def setWordWrap(self, wrap: bool):
        """兼容QLabel的setWordWrap方法"""
        self._word_wrap = wrap
        if wrap:
            self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    def wordWrap(self) -> bool:
        """兼容QLabel的wordWrap方法"""
        return self._word_wrap
    
    def setAlignment(self, alignment):
        """兼容QLabel的setAlignment方法"""
        # 通过CSS设置对齐方式
        if alignment == Qt.AlignmentFlag.AlignCenter:
            text_align = "center"
        elif alignment == Qt.AlignmentFlag.AlignRight:
            text_align = "right"
        else:
            text_align = "left"
        
        # 重新渲染内容以应用对齐
        current_content = self._content
        if current_content:
            self.set_content(current_content)
    
    def clear(self):
        """清空内容"""
        self._content = ""
        self.setHtml("")
        self.contentChanged.emit()
    
    def isEmpty(self) -> bool:
        """检查是否为空"""
        return not bool(self._content)
    
    # 样式设置方法    def setMaximumWidth(self, width: int):
        """设置最大宽度"""
        self._max_width = width
        # 不调用 super().setMaximumWidth() 因为我们要控制实际宽度
        QTimer.singleShot(1, self._adjust_height)
    def setBackgroundColor(self, color: str):
        """设置背景颜色"""
        self._background_color = color
        self._update_widget_style()
        if self._content:
            self.set_content(self._content)
    
    def setBorderRadius(self, radius: int):
        """设置圆角半径"""
        self._border_radius = radius
        self._update_widget_style()
        if self._content:
            self.set_content(self._content)
    
    def setPadding(self, padding: int):
        """设置内边距"""
        self._padding = padding
        self._update_widget_style()
        if self._content:
            self.set_content(self._content)
    
    def setFontSize(self, size: int):
        """设置字体大小"""
        self._font_size = size
        if self._content:
            self.set_content(self._content)
    
    def setMinHeight(self, height: int):
        """设置最小高度"""
        self._min_height = height
        QTimer.singleShot(1, self._adjust_height)
    
    # 获取属性方法
    def getBackgroundColor(self) -> str:
        return self._background_color
    
    def getBorderRadius(self) -> int:
        return self._border_radius
    
    def getPadding(self) -> int:
        return self._padding
    
    def getFontSize(self) -> int:
        return self._font_size
    def getMaxWidth(self) -> int:
        return self._max_width
    
    def isMarkdown(self) -> bool:
        """检查当前内容是否为Markdown格式"""
        return self._is_markdown
    
    def getContent(self) -> str:
        """获取原始内容"""
        return self._content
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 处理链接悬停效果"""
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QCursor
        
        # 获取鼠标位置处的锚点（链接）
        cursor = self.cursorForPosition(event.pos())
        char_format = cursor.charFormat()
        
        if char_format.isAnchor():
            # 鼠标在链接上
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            # 这里可以添加更多悬停效果，但QTextEdit的限制比较大
        else:
            # 鼠标不在链接上
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """鼠标点击事件 - 处理链接点击"""
        from PyQt6.QtCore import Qt
        
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            char_format = cursor.charFormat()
            
            if char_format.isAnchor():
                # 点击了链接
                link_url = char_format.anchorHref()
                if link_url:
                    self._open_link(link_url)
                    return
        
        super().mousePressEvent(event)
    
    def _open_link(self, url: str):
        """打开链接"""
        try:
            import webbrowser
            webbrowser.open(url)
            print(f"打开链接: {url}")
        except Exception as e:
            print(f"无法打开链接 {url}: {e}")


class BubbleTextWidget(AdvancedTextWidget):
    """
    气泡样式的文本组件
    专门用于聊天消息显示
    """
    
    def __init__(self, parent=None, align_right: bool = False):
        super().__init__(parent)
        
        self.align_right = align_right
        self._setup_bubble_style()
    
    def _setup_bubble_style(self):
        """设置气泡样式"""
        # 根据对齐方向设置不同的颜色
        if self.align_right:
            self.setBackgroundColor('#a0e6a0')  # 用户消息：绿色
        else:
            self.setBackgroundColor('white')    # AI消息：白色
        
        # 设置圆角和内边距
        self.setBorderRadius(15)
        self.setPadding(12)
        
        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
    
    def set_message_content(self, content: str, is_user: bool = None):
        """
        设置消息内容
        
        Args:
            content: 消息内容
            is_user: 是否为用户消息，None时使用初始化时的设置
        """
        if is_user is not None:
            self.align_right = is_user
            self._setup_bubble_style()
        
        # 用户消息强制为普通文本，AI消息自动检测
        if self.align_right:
            self.set_plain_content(content)
        else:
            self.set_content(content)
