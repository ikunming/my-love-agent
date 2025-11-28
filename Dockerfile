# 1. 使用官方 Python 轻量镜像
FROM python:3.11-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 设置环境变量 (防止 Python 生成 .pyc 文件，让日志直接输出)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. 安装系统依赖 (如果你的 PDF 生成工具需要 wkhtmltopdf 或其他库，在这里加)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制项目所有代码
COPY . .

# 7. 暴露端口
EXPOSE 8080

# 8. 启动命令 (跟你在本地运行的命令类似，但 host 改为 0.0.0.0)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]