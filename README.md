# Nefelibata

Nefelibata 是一个基于 Python 和 PyQt6 开发的智能聊天应用程序，支持多种大语言模型，提供自然流畅的对话体验。

## 功能特点

- 支持最新的 GLM 和 DeepSeek 模型
- 自然流畅的用户界面交互
- 数据安全加密存储
- 聊天历史记录管理
- 多模型切换支持
- 消息复制和删除功能

## 环境要求

- Python 3.8+
- PyQt6
- SQLite3

## 安装步骤

1. 克隆项目到本地：
```bash {executable}
git clone https://github.com/KercyDing/Nefelibata.git
```

```bash {executable}
cd Nefelibata
```

2. 安装依赖：
```bash {executable}
pip install -r requirements.txt
```

## 配置说明

### API 密钥配置

1. 在应用程序中点击右上角的密钥图标
2. 在弹出的对话框中填入对应的 API Key：
   - GLM API Key（支持 glm-4 系列模型）
   - DeepSeek API Key（支持 DeepSeek 系列模型）

### 模型选择

1. 点击右上角的设置图标
2. 在模型选择对话框中选择需要使用的模型：

支持的模型列表：
- GLM 系列：
  - glm-4-flash（免费版）
  - glm-4-flashx（高速低价版）
  - glm-4-air（性价比版）
  - glm-4-plus（旗舰版）
- DeepSeek 系列：
  - DeepSeek-V3（快速精准版）
  - DeepSeek-R1（最强推理版）

## 使用说明

1. 启动应用：
```bash {executable}
python main.py
```

2. 基本操作：
- 发送消息：在底部输入框输入内容，点击发送按钮或按回车键发送
- 复制消息：点击消息左下角的复制图标
- 删除消息：点击消息左下角的删除图标
- 清空历史：点击右下角的清除按钮

## 数据安全

- API 密钥采用加密存储
- 聊天记录本地存储在 SQLite 数据库中
- 支持消息的安全删除

## 版本信息

当前版本：v1.0.0

## 创作团队
[KercyDing](https://github.com/KercyDing) 和 [wsh051123](https://github.com/wsh051123)

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件至：[dkx215417@gmail.com] 和 [1758407550@qq.com]
