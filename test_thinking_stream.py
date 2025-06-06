#!/usr/bin/env python3
"""
测试GLM-Z1思考过程流式处理功能
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QScrollArea
from PyQt6.QtCore import QTimer
from ui.widgets import MessageWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLM-Z1 思考过程流式测试")
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
        test_button = QPushButton("开始流式思考测试")
        test_button.clicked.connect(self.start_streaming_test)
        layout.addWidget(test_button)
        
        self.current_message_widget = None        self.test_content_chunks = [
            "<think>",
            "我需要仔细分析这个问题。",
            "首先，让我理解用户的需求：",
            "1. 思考过程中不应该显示正常气泡框",
            "2. 不应该显示</think>标签",
            "3. 只有思考气泡框应该可见",
            "现在我来验证这个实现...",
            "</think>",
            "很好！现在思考过程已经正确实现了！",
            "\n\n✅ **修复要点：**",
            "\n1. **思考模式时隐藏正常气泡框**",
            "\n2. **完全过滤掉</think>标签**", 
            "\n3. **思考完成后显示正常内容**",
            "\n\n现在用户体验应该很流畅了！"
        ]
        self.chunk_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.send_next_chunk)
        
    def start_streaming_test(self):
        """开始流式测试"""
        # 创建新的AI消息组件
        self.current_message_widget = MessageWidget("", align_right=False, parent=self)
        self.message_layout.insertWidget(self.message_layout.count() - 1, self.current_message_widget)
        
        # 重置测试状态
        self.chunk_index = 0
        
        # 开始定时发送内容块
        self.timer.start(300)  # 每300ms发送一个内容块
        
    def send_next_chunk(self):
        """发送下一个内容块"""
        if self.chunk_index < len(self.test_content_chunks):
            chunk = self.test_content_chunks[self.chunk_index]
            print(f"发送块 {self.chunk_index}: {repr(chunk)}")
            
            # 模拟流式更新
            if self.current_message_widget:
                self.current_message_widget.append_content(chunk)
            
            self.chunk_index += 1
        else:
            # 测试完成
            self.timer.stop()
            print("流式测试完成！")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    print("GLM-Z1 思考过程流式处理测试")
    print("点击按钮开始测试...")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
