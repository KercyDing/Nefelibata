#!/usr/bin/env python3
"""
最终验证测试 - 验证三个关键修复
1. 圆角矩形包装无空白行 (CSS布局问题)
2. 链接悬停效果和点击打开浏览器功能
3. 表格渲染正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QScrollArea
from PyQt6.QtCore import Qt
from ui.advanced_text_widget import AdvancedTextWidget, BubbleTextWidget

class FinalValidationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("最终验证测试 - 三个关键修复")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
          # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(scroll)
        
        # 滚动内容
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 标题
        title = QLabel("🔍 最终验证测试 - 验证三个关键修复")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px; color: #2c3e50;")
        scroll_layout.addWidget(title)
        
        # === 测试1: 圆角矩形无空白行 ===
        self.add_test_section(scroll_layout, "1️⃣ 圆角矩形包装无空白行测试", self.test_round_corners_no_blanks)
        
        # === 测试2: 链接功能 ===
        self.add_test_section(scroll_layout, "2️⃣ 链接悬停与点击功能测试", self.test_link_functionality)
        
        # === 测试3: 表格渲染 ===
        self.add_test_section(scroll_layout, "3️⃣ 表格渲染功能测试", self.test_table_rendering)
        
        scroll.setWidget(scroll_widget)
        
    def add_test_section(self, layout, title, test_func):
        """添加测试区域"""
        # 区域标题
        section_title = QLabel(title)
        section_title.setStyleSheet("""
            font-size: 16px; 
            font-weight: bold; 
            margin: 20px 10px 10px 10px; 
            color: #34495e;
            background-color: #ecf0f1;
            padding: 8px;
            border-radius: 4px;
        """)
        layout.addWidget(section_title)
        
        # 执行测试
        test_func(layout)
        
    def test_round_corners_no_blanks(self, layout):
        """测试1: 圆角矩形包装无空白行"""        # 单段落测试 - 不应有多余空白
        widget1 = BubbleTextWidget()
        widget1.set_content("这是一个单段落测试。应该没有多余的空白行在圆角矩形内。")
        widget1.setBackgroundColor("#e8f5e8")
        widget1.setBorderRadius(15)
        widget1.setPadding(12)
        layout.addWidget(widget1)
        
        # 多段落测试 - 段落间距应该适中
        widget2 = BubbleTextWidget()
        widget2.set_content("""第一段落内容。
        
第二段落内容。

第三段落内容。""")
        widget2.setBackgroundColor("#fff2e8")
        widget2.setBorderRadius(20)
        widget2.setPadding(15)
        layout.addWidget(widget2)
          # Markdown单段落测试
        widget3 = BubbleTextWidget()
        widget3.set_content("**粗体文本** 和 *斜体文本* 在单段落中，不应有多余空白。")
        widget3.setBackgroundColor("#e8f0ff")
        widget3.setBorderRadius(12)
        widget3.setPadding(10)
        layout.addWidget(widget3)    
        
    def test_link_functionality(self, layout):
        """测试2: 链接悬停与点击功能"""        
        # Markdown链接测试
        widget = BubbleTextWidget()
        widget.set_content("""
## Markdown链接测试

请点击以下链接测试功能：

- [GitHub主页](https://www.github.com) - 点击应打开浏览器
- [Python官网](https://www.python.org) - 悬停应有背景效果
- [百度搜索](https://www.baidu.com) - 应该可以点击打开
- [Google搜索](https://www.google.com) - 悬停时应有效果
- [Stack Overflow](https://www.stackoverflow.com) - 测试链接交互

**注意观察**：
1. 悬停时链接背景变化
2. 点击时是否正确打开浏览器
3. 链接颜色和样式是否正确
        """)
        widget.setBackgroundColor("#fff5f5")
        widget.setBorderRadius(10)
        widget.setPadding(12)
        layout.addWidget(widget)
    
    def test_table_rendering(self, layout):
        """测试3: 表格渲染功能"""        
        # Markdown表格测试
        widget1 = AdvancedTextWidget()
        widget1.set_content("""
### 基本表格渲染测试

| 姓名 | 年龄 | 职业 | 城市 |
|------|------|------|------|
| 张三 | 25 | 工程师 | 北京 |
| 李四 | 30 | 设计师 | 上海 |
| 王五 | 28 | 产品经理 | 深圳 |

**请检查**：表格边框、行悬停效果、对齐方式
        """)
        widget1.setBackgroundColor("#f0f8ff")
        widget1.setBorderRadius(8)
        widget1.setPadding(15)
        layout.addWidget(widget1)
          # Markdown表格测试
        widget2 = BubbleTextWidget()
        widget2.set_content("""
### Markdown表格渲染测试

| 功能特性 | 状态 | 优先级 | 备注 |
|---------|------|--------|------|
| 圆角矩形 | ✅ 完成 | 高 | 无空白行问题已修复 |
| 链接功能 | ✅ 完成 | 高 | 悬停和点击都正常 |
| 表格渲染 | 🧪 测试中 | 高 | 正在验证此功能 |
| 自动高度 | ✅ 完成 | 中 | 内容变化时自适应 |
| Markdown | ✅ 完成 | 中 | 支持所有标准语法 |

**表格测试要点**：
1. ✨ 边框应该清晰可见
2. 🎨 鼠标悬停行应该高亮
3. 📏 列对齐应该正确
4. 🌈 交替行颜色应该显示
        """)
        widget2.setBackgroundColor("#f0fff0")
        widget2.setBorderRadius(12)
        widget2.setPadding(15)
        layout.addWidget(widget2)        # 复杂表格测试
        widget3 = AdvancedTextWidget()
        widget3.set_content("""
### 复杂表格功能测试

| 姓名 | 部门 | 邮箱 | 电话 |
|------|------|------|------|
| **张三** | 技术部 | [zhang@example.com](mailto:zhang@example.com) | 138-0000-0001 |
| *李四* | 设计部 | [li@example.com](mailto:li@example.com) | 138-0000-0002 |

*此表格包含格式化文本和链接*
        """)
        widget3.setBackgroundColor("#fffacd")
        widget3.setBorderRadius(10)
        widget3.setPadding(12)
        layout.addWidget(widget3)

def main():
    app = QApplication(sys.argv)
    
    print("🚀 启动最终验证测试...")
    print("\n" + "="*60)
    print("📋 验证清单：")
    print("1. ✅ 圆角矩形包装无空白行")
    print("2. ✅ 链接悬停效果和点击功能")
    print("3. ✅ 表格渲染正常工作")
    print("="*60)
    print("\n💡 测试说明：")
    print("- 观察圆角气泡是否有多余空白行")
    print("- 尝试悬停和点击各种链接")
    print("- 检查表格的边框、悬停效果和对齐")
    print("- 滚动查看所有测试内容")
    print("\n🎯 如果所有功能正常，说明三个关键问题已全部修复！\n")
    
    window = FinalValidationWindow()
    window.show()
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
