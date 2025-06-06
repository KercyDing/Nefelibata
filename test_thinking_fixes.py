#!/usr/bin/env python3
"""
测试修复后的thinking处理功能
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QScrollArea
from ui.widgets import MessageWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("思考内容处理测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主界面
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.addStretch()
        scroll_area.setWidget(self.message_container)
        layout.addWidget(scroll_area)
        
        # 创建测试按钮
        test_button1 = QPushButton("测试静态thinking内容")
        test_button1.clicked.connect(self.test_static_thinking)
        layout.addWidget(test_button1)
        
        test_button2 = QPushButton("测试流式thinking内容")
        test_button2.clicked.connect(self.test_streaming_thinking)
        layout.addWidget(test_button2)
        
    def test_static_thinking(self):
        """测试静态thinking内容解析"""
        # 模拟从数据库加载的完整消息
        test_content = """前面的内容<think>我需要分析这个问题：
1. 用户询问了什么
2. 如何最好地回答
3. 需要注意什么细节

现在我来组织答案...</think>后面的正常回复内容。

这是最终的答案！"""
        
        # 创建AI消息组件（模拟静态加载）
        message_widget = MessageWidget(test_content, align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
        print("已添加静态thinking测试消息")
        
    def test_streaming_thinking(self):
        """测试流式thinking内容（不自动隐藏）"""
        # 创建新的AI消息组件
        message_widget = MessageWidget("", align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message_widget)
        
        # 模拟流式内容
        test_chunks = [
            "开始回复",
            "<think>",
            "让我思考这个问题...",
            "用户想要的是...",
            "我应该这样回答...",
            "</think>",
            "很好的问题！",
            "\n\n根据分析，答案是这样的..."
        ]
        
        full_content = ""
        for chunk in test_chunks:
            full_content += chunk
            message_widget.append_content(chunk)
            # 模拟延迟
            QApplication.processEvents()
        
        print("已完成流式thinking测试")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("思考内容处理测试")
    print("测试项目：")
    print("1. 静态thinking内容不应该出现在正常气泡中")
    print("2. 思考过程完成后不应该自动隐藏")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
