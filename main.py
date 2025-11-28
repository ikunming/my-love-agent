"""
FastAPI 主应用
"""
import sys
import os
from fastapi.staticfiles import StaticFiles

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import json

from agent import runner, session_service
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# 创建 FastAPI 应用
app = FastAPI(title="Google ADK Agent API", version="1.0.0",debug=True)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------
# 【Vue 前端挂载配置】
# ----------------------------------------------------------------

# 1. 定位 dist 文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

if os.path.exists(DIST_DIR):
    # 2. 挂载静态资源 (js, css, img)
    # Vue 打包后通常会把静态资源放在 dist/assets 目录下
    # 我们把它挂载到 /assets 路径，这样 index.html 里的引用就能找到文件了
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")


    # 3. 处理根路由和所有“未知路由” (Vue Router 专用模式)
    # 无论用户访问 / 还是 /chat 还是 /login，都返回 index.html
    # 让 Vue 在前端自己去跳转页面
    @app.get("/{full_path:path}")
    async def serve_vue_app(full_path: str):
        # 如果请求的是 API，跳过这里 (FastAPI 会自动优先匹配上面的 API 路由)
        if full_path.startswith("api/"):
            return {"error": "API route not found"}

        # 否则返回 index.html
        return FileResponse(os.path.join(DIST_DIR, "index.html"))

else:
    print(f"⚠️ 警告: 找不到 dist 文件夹。请确保你已经运行了 npm run build 并把 dist 放到根目录。")

# 配置流式模式
run_config = RunConfig(streaming_mode=StreamingMode.SSE)


# 数据模型
class ChatRequest(BaseModel):
    message: str = Field(..., description="用户消息")
    user_id: str = Field(default="user", description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    stream: bool = Field(default=True, description="是否流式响应")


class SessionCreate(BaseModel):
    user_id: str = Field(default="user", description="用户ID")
    app_name: str = Field(default="agent", description="应用名称")


# API 路由
@app.get("/")
async def root():
    return {"message": "Google ADK Agent API", "version": "1.0.0"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/create_session")
async def create_session(request: SessionCreate):
    """创建新会话"""
    try:
        session = await session_service.create_session(
            user_id=request.user_id,
            app_name=request.app_name
        )
        return {"session_id": session.id, "user_id": request.user_id, "app_name": request.app_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """与 Agent 对话"""
    try:
        # 如果没有 session_id，创建新会话
        session_id = request.session_id
        if not session_id:
            session = await session_service.create_session(
                user_id=request.user_id,
                app_name="agent"
            )
            session_id = session.id
        
        content = types.Content(role="user", parts=[types.Part(text=request.message)])
        
        # 流式响应
        if request.stream:
            async def event_generator():
                try:
                    yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
                    
                    # 使用 run_async 进行流式输出
                    async for event in runner.run_async(
                        user_id=request.user_id,
                        session_id=session_id,
                        new_message=content,
                        run_config=run_config
                    ):
                        # 提取文本内容
                        if event.content and event.content.parts:
                            for part in event.content.parts:
                                if part.text:
                                    yield f"data: {json.dumps({'type': 'message', 'content': part.text})}\n\n"
                    
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        
        # 非流式响应
        else:
            full_response = ""
            
            # 使用 run_async 收集完整响应
            async for event in runner.run_async(
                user_id=request.user_id,
                session_id=session_id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            full_response += part.text
            
            return {"session_id": session_id, "message": full_response, "user_id": request.user_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download_pdf/{file_name}")
async def download_pdf(file_name: str):
    """下载生成的 PDF 文件"""
    try:
        # 获取 PDF 输出目录
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_dir = os.path.join(base_dir, "generated_pdfs")
        file_path = os.path.join(pdf_dir, file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF 文件不存在")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=file_name,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/list_pdfs")
async def list_pdfs():
    """列出所有生成的 PDF 文件"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_dir = os.path.join(base_dir, "generated_pdfs")
        
        # 确保目录存在
        if not os.path.exists(pdf_dir):
            return {"pdfs": []}
        
        # 获取所有 PDF 文件
        pdf_files = []
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                file_path = os.path.join(pdf_dir, file)
                file_stat = os.stat(file_path)
                pdf_files.append({
                    "name": file,
                    "size": file_stat.st_size,
                    "created_at": file_stat.st_ctime,
                    "download_url": f"/api/download_pdf/{file}"
                })
        
        # 按创建时间倒序排列
        pdf_files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"pdfs": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("api.main:app", host="0.0.0.0", port=8080, reload=True)
