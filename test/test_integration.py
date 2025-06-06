#!/usr/bin/env python3
"""
测试新气泡消息组件在主程序中的集成
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt6.QtCore import QTimer
from ui.bubble_message_widget import BubbleMessageWidget, ThinkingBubbleWidget


class MainIntegrationTestWindow(QMainWindow):
    """主程序集成测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("气泡消息组件集成测试")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        
        # 测试按钮
        self.add_user_btn = QPushButton("添加用户消息")
        self.add_ai_btn = QPushButton("添加AI消息") 
        self.add_markdown_btn = QPushButton("添加Markdown消息")
        self.add_thinking_btn = QPushButton("添加思考消息")
        self.add_table_btn = QPushButton("添加表格消息")
        self.add_links_btn = QPushButton("添加链接消息")
        self.test_stream_btn = QPushButton("测试流式更新")
        self.clear_btn = QPushButton("清空消息")
        
        button_layout.addWidget(self.add_user_btn)
        button_layout.addWidget(self.add_ai_btn)
        button_layout.addWidget(self.add_markdown_btn)
        button_layout.addWidget(self.add_thinking_btn)
        button_layout.addWidget(self.add_table_btn)
        button_layout.addWidget(self.add_links_btn)
        button_layout.addWidget(self.test_stream_btn)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # 创建消息容器
        self.message_widget = QWidget()
        self.message_layout = QVBoxLayout(self.message_widget)
        self.message_layout.setSpacing(10)
        self.message_layout.setContentsMargins(20, 20, 20, 20)
        self.message_layout.addStretch()  # 消息向上对齐
        
        main_layout.addWidget(self.message_widget)
        
        # 连接按钮事件
        self.add_user_btn.clicked.connect(self.add_user_message)
        self.add_ai_btn.clicked.connect(self.add_ai_message)
        self.add_markdown_btn.clicked.connect(self.add_markdown_message)
        self.add_thinking_btn.clicked.connect(self.add_thinking_message)
        self.add_table_btn.clicked.connect(self.add_table_message)
        self.add_links_btn.clicked.connect(self.add_links_message)
        self.test_stream_btn.clicked.connect(self.test_streaming)
        self.clear_btn.clicked.connect(self.clear_messages)
        
        # 流式更新测试相关
        self.current_stream_widget = None
        self.stream_content = ""
        self.stream_timer = QTimer()
        self.stream_timer.timeout.connect(self.update_stream)
        self.stream_index = 0
        
    def add_user_message(self):
        """添加用户消息"""
        content = "这是一条用户消息。用户消息通常显示为绿色气泡，并且位于右侧。"
        message_widget = BubbleMessageWidget(content, align_right=True, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
    def add_ai_message(self):
        """添加AI消息"""
        content = "这是一条AI回复消息。AI消息显示为白色气泡，位于左侧，支持Markdown格式。"
        message_widget = BubbleMessageWidget(content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
    
    def add_markdown_message(self):
        """添加Markdown消息"""
        content = """这是一个包含**Markdown格式**的消息：

## 主要特性

1. **粗体文本**和*斜体文本*
2. `内联代码`示例
3. 支持列表和标题

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

这些格式都能正确渲染！"""
        message_widget = BubbleMessageWidget(content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
    
    def add_thinking_message(self):
        """添加包含思考过程的消息"""
        content = """<think>
让我想想这个问题...
首先，我需要分析用户的需求。
然后，我需要提供一个合适的解决方案。
最后，我要确保答案清晰易懂。
</think>

根据你的问题，我建议采用以下方法：

1. 首先分析需求
2. 然后制定计划  
3. 最后执行方案

这样的步骤可以确保项目成功。"""
        message_widget = BubbleMessageWidget(content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
    
    def add_table_message(self):
        """添加表格消息"""
        content = """以下是一个表格示例：

| 特性 | 旧组件 | 新组件 |
|------|--------|--------|
| Markdown支持 | 基础 | 完整 |
| 表格渲染 | 有问题 | 完美 |
| 链接功能 | 基础 | 增强 |
| 样式控制 | 有限 | 灵活 |
| 性能 | 一般 | 优秀 |

表格现在可以正确渲染，包括边框、悬停效果和交替行颜色！"""
        message_widget = BubbleMessageWidget(content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
    
    def add_links_message(self):
        """添加链接消息"""
        content = """这里有一些链接测试：

- 官方网站：[GitHub](https://github.com)
- 搜索引擎：[Google](https://google.com)  
- 技术文档：[PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- 本地链接：[localhost](http://localhost:3000)

现在链接有正确的悬停效果，点击可以在浏览器中打开！"""
        message_widget = BubbleMessageWidget(content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
    
    def test_streaming(self):
        """测试流式更新"""
        if self.stream_timer.isActive():
            self.stream_timer.stop()
            self.test_stream_btn.setText("测试流式更新")
            return
            
        # 准备流式内容
        self.stream_content = """<think>
用户要求测试流式更新功能...
我需要逐步展示内容，模拟真实的AI回复过程。
这样可以验证thinking功能和流式更新是否正常工作。
</think>

让我为你演示流式更新功能：

## 实时更新测试

这是第一段内容，然后会逐步添加更多内容...

**第二段内容**：流式更新可以让用户实时看到AI的回复过程。

```python
# 第三段：代码示例
def streaming_demo():
    for chunk in response_chunks:
        yield chunk
```

最后一段：所有内容都已经显示完毕！"""
        
        # 创建新的流式消息组件
        self.current_stream_widget = BubbleMessageWidget("", align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, self.current_stream_widget)
        
        # 开始流式更新
        self.stream_index = 0
        self.stream_timer.start(100)  # 每100ms更新一次
        self.test_stream_btn.setText("停止流式更新")
    
    def update_stream(self):
        """更新流式内容"""
        if self.stream_index < len(self.stream_content):
            # 逐字符添加内容（模拟真实流式更新）
            chunk_size = 3  # 每次添加3个字符
            chunk = self.stream_content[self.stream_index:self.stream_index + chunk_size]
            
            current_content = self.stream_content[:self.stream_index + len(chunk)]
            self.current_stream_widget.update_content(current_content)
            
            self.stream_index += len(chunk)
        else:
            # 流式更新完成
            self.stream_timer.stop()
            self.test_stream_btn.setText("测试流式更新")
            self.current_stream_widget = None
    
    def clear_messages(self):
        """清空所有消息"""
        # 停止流式更新
        if self.stream_timer.isActive():
            self.stream_timer.stop()
            self.test_stream_btn.setText("测试流式更新")
        
        # 移除所有消息组件
        while self.message_layout.count() > 1:  # 保留最后的stretch
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def copy_message_content(self, content: str):
        """复制消息内容（兼容接口）"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        print(f"已复制内容: {content[:50]}...")
    
    def delete_message(self, message_widget):
        """删除消息（兼容接口）"""
        self.message_layout.removeWidget(message_widget)
        message_widget.deleteLater()
        print("消息已删除")


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)
    
    window = MainIntegrationTestWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
