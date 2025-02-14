import sqlite3
import os
from datetime import datetime

class ChatDatabase:
    def __init__(self):
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 数据库文件路径
        self.db_path = os.path.join(current_dir, 'chat_history.db')
        self.init_database()

    def init_database(self):
        """初始化数据库，创建消息表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                sender TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                conversation_id TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_message(self, content, sender, conversation_id):
        """保存新消息到数据库，并维持最多50条消息的限制"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查当前消息总数
        cursor.execute('SELECT COUNT(*) FROM messages WHERE conversation_id = ?', (conversation_id,))
        count = cursor.fetchone()[0]
        
        # 如果消息数量达到50条，删除最早的消息
        if count >= 50:
            cursor.execute('''
                DELETE FROM messages 
                WHERE id IN (
                    SELECT id FROM messages 
                    WHERE conversation_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT 1
                )
            ''', (conversation_id,))
        
        # 插入新消息
        cursor.execute('''
            INSERT INTO messages (content, sender, conversation_id)
            VALUES (?, ?, ?)
        ''', (content, sender, conversation_id))
        
        # 获取新插入消息的ID
        message_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return message_id

    def get_conversation_history(self, conversation_id, limit=50):
        """获取指定会话的历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, sender, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (conversation_id, limit))
        
        messages = cursor.fetchall()
        conn.close()
        
        # 将消息记录转换
        formatted_messages = []
        for message_id, content, sender, _ in reversed(messages):
            formatted_messages.append({
                "id": message_id,
                "role": "assistant" if sender == "ai" else "user",
                "content": content
            })
        
        return formatted_messages

    def delete_message(self, message_id):
        """从数据库中删除指定消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        
        conn.commit()
        conn.close()