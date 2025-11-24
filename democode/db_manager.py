import sqlite3
from datetime import datetime

# 数据库文件名（会自动在当前文件夹生成）
DB_FILE = "love_ai_memory.db"


def init_db():
    """初始化数据库：如果是第一次运行，会创建一个表"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 创建一个简单的表：记录是谁(role)在什么时候(timestamp)说了什么(content)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    print(f"✅ 数据库 {DB_FILE} 就绪。")


def save_message(user_id, role, content):
    """保存一条消息"""
    # role 建议用 'user' 代表用户，'model' 代表 AI
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, role, content, datetime.now()))
    conn.commit()
    conn.close()
    print(f"💾 已保存 [{role}]: {content[:10]}...")


def get_recent_history(user_id, limit=5):
    """获取最近的 N 条记录，构建上下文给 AI"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 按时间倒序取最近的 limit 条
    cursor.execute('''
        SELECT role, content FROM chat_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    # 数据库取出来是[最新, 次新...]，但发给 AI 需要按时间正序[老, ... , 新]
    # 所以这里用 [::-1] 翻转一下列表
    return rows[::-1]


# --- 以下是模拟运行代码 (你可以直接运行这个文件看效果) ---

if __name__ == "__main__":
    # 1. 初始化
    init_db()

    # 假设当前用户ID是 "boyfriend_01"
    current_user = "boyfriend_01"

    # 2. 模拟：用户发了一句话
    user_input = "我女朋友说只要我开心她就开心，这是什么意思？"
    save_message(current_user, "user", user_input)

    # 3. 模拟：你的 ADK/Gemini 思考后，回复了一句话
    ai_reply = "这是陷阱题！千万别信。她在反讽，意思是让你关注她的感受。"
    save_message(current_user, "model", ai_reply)

    print("-" * 30)
    print("🔍 正在提取历史记录准备发送给 API...")

    # 4. 提取历史记录（模拟构建 Prompt）
    history = get_recent_history(current_user, limit=10)

    formatted_context = []
    for role, content in history:
        formatted_context.append(f"{role}: {content}")

    print("\n".join(formatted_context))