FROM node:20-bookworm-slim AS node-runtime

FROM python:3.12-slim
WORKDIR /app

# 沙箱仅需 node 运行时，从官方镜像复制二进制，避免 apt 安装 npm 全家桶
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
