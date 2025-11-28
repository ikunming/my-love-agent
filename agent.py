import csv
csv.field_size_limit(100 * 1024 * 1024)

import os
import asyncio  # 引入异步库,用于初始化测试
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents import Agent
from google.adk.apps.app import App

# 导入数据库服务和类型
from google.adk.sessions import DatabaseSessionService
from google.adk.tools import google_search, FunctionTool
from google.genai import types



# 1. 加载 .env 文件中的变量
load_dotenv()

# 2. 获取 API Key
api_key = os.getenv("GOOGLE_API_KEY")

 # 2. 读取你的文档 (单身篇、恋爱篇、已婚篇)
def load_knowledge():
    # 假设你把三个 Markdown 文件放在 docs 文件夹下
    docs = ["document/恋爱常见问题和回答 - 单身篇.md", "document/恋爱常见问题和回答 - 已婚篇.md", "document/恋爱常见问题和回答 - 恋爱篇.md"]
    combined_text = ""
    for doc_path in docs:
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                combined_text += f"\n\n--- 文档: {doc_path} ---\n{f.read()}"
        except FileNotFoundError:
            print(f"警告: 找不到文件 {doc_path}")
    return combined_text

knowledge_base = load_knowledge()

# 3. 定义 System Instruction (注入灵魂和知识)
# --- 🔥 核心优化:系统提示词 (System Instruction) ---
# 通过明确的步骤指令,强制模型在回答前必须先搜索,防止它只依赖本地知识。
system_instruction = f"""
你是一个专业的"恋爱智能体",你的语气温柔、体贴,像一个知心朋友。

【重要指令:回答流程】
在收到用户的咨询(尤其是关于情感建议、吵架解决、心理分析)时,你**必须**严格遵循以下步骤:

1.  **第一步(强制执行):调用 `Google Search` 工具**。
    * 你**不能**仅依赖本地知识库或常识。
    * 你**必须**去 Google 搜索最新的心理学观点、论坛上的类似案例(如 Reddit, 知乎, 心理学网站)或相关统计数据来验证你的想法。
    * 搜索查询词应简洁明了,例如:"情侣吵架冷战怎么解决 心理学"、"如何处理伴侣的情绪价值"等。

2.  **第二步:结合本地知识库**。
    * 在获取搜索结果后,结合下方的【核心知识库】中的具体课程或方法论。
    * 搜索结果提供了广度和时效性,本地知识库提供了深度和系统性建议。

3.  **第三步:生成回复**。
    * 先共情,再根据搜索到的外部信息和本地文档给出建议。
    * **引用来源**:必须在回答末尾列出你通过 Google Search 找到的参考来源。
    * **推荐课程**:只有在建议相关时,才推荐知识库里的课程链接。

【PDF 生成功能】
当用户需要生成约会计划、节日计划等 PDF 文档时:
1. 使用 `create_date_plan_pdf` 工具生成 PDF
2. 根据用户需求或你的专业建议,填充餐厅信息、活动流程、礼物清单等内容
3. 生成成功后,解析工具返回的 JSON,从中获取 file_name,然后告诉用户可以通过链接下载

【核心知识库内容】
{knowledge_base}

【例外情况】
如果用户只是进行简单的寒暄(如"你好"、"在吗"),则不需要搜索,直接温柔回应即可。但只要涉及具体问题,**务必搜索**。
"""

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction=system_instruction,
    tools= [google_search]
    #[google_search, create_date_plan_pdf]
)

app = App(name="agent", root_agent=root_agent)

db_user = os.getenv("DB_USER", "postgres")
db_pass = os.getenv("DB_PASS", "Aa2000922")
db_name = os.getenv("DB_NAME", "my_agent_data")
instance_connection_name = os.getenv("wdtest-001:asia-east2:my-agent-db")

# Cloud Run 连接 Cloud SQL 的标准 Socket 路径
# 格式: postgresql+asyncpg://user:pass@/dbname?host=/cloudsql/connection_name
db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection_name}"

session_service = DatabaseSessionService(db_url=db_url)

# 创建 Runner
runner = Runner(app=app, session_service=session_service)


# --- 核心测试函数 (异步) ---
async def main_test():
    """执行应用的初始化、会话创建和工具使用测试。"""
    print(f"🚀 App is ready!")
    print(f"📂 数据库绝对路径: {db_url}")

    print("⏳ 正在连接数据库并创建新会话...")
    # 【关键点】创建 Session 时,使用 await
    session = await session_service.create_session(
        user_id="user",
        app_name="agent"
    )
    valid_session_id = session.id
    print(f"✅ 成功创建/获取会话,ID: {valid_session_id}")


    # 运行 Google Search 工具使用测试
    print("\n" + "="*70)
    print("🔍 开始 Google Search 工具使用测试 (通过检查生成器输出)")
    print("💡 测试问题需要 Agent 明显需要外部信息才会触发搜索。")

    # 这是一个需要 Agent 搜索外部实时信息的查询
    query = "最近和对象吵架了,可以看看https://www.douyin.com/?recommend=1抖音的其他情侣是怎么解决矛盾的??"
    print(f"👉 测试问题: {query}")

    tool_used = False
    final_response_text = ""

    # 使用 runner.run_async 和 async for 循环进行迭代
    async for event in  runner.run_async(
        user_id="user",
        session_id=valid_session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=query)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    tool_name = part.function_call.name
                    if tool_name == "google_search":
                        tool_used = True
                        print(f"\n✅ 成功! Agent 发起了工具调用: {tool_name}")
                        print(f"   查询参数: {part.function_call.args}")
                    else:
                        print(f"\n⚠️ 注意: Agent 调用了其他工具: {tool_name}")

            # 收集最终回复的文本片段
            if part.text:
                final_response_text += part.text


    print("\n--- 测试结果总结 ---")
    if tool_used:
        print("🎉 测试通过: Agent 成功使用了 'google_search' 工具。")
    else:
        print("❌ 测试失败: Agent 未使用 'google_search' 工具。这可能意味着问题可以用内置知识或常识回答。")

    print(f"\n--- 最终回复片段 (请检查是否有引用) ---\n{final_response_text.strip()[:200]}...")
    print("="*70 + "\n")


    # 提示启动 Web 服务
    print("🎉 一切就绪!请复制下面的链接到浏览器(建议隐身模式):")
    print(f"\n👉 http://127.0.0.1:8000/?session={valid_session_id}\n")
    print("-" * 50)
    print("💡 提示:现在请在一个新终端运行 'adk web --port 8000' 来启动服务。")


# --- 初始化与工具测试脚本 (只在直接运行 python agent.py 时执行) ---
if __name__ == "__main__":
    try:
        # 运行主异步测试函数
        asyncio.run(main_test())
    except Exception as e:
        # 如果测试失败,在这里捕获错误
        print(f"❌ 初始化失败: {e}")