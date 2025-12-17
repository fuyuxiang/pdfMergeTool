# PDF合并小工具

功能：
- 浏览器上传多个 PDF
- 服务器端按选择顺序合并
- 合并完成后立即下载
- 默认仅在内存中处理，不写入磁盘

## 1) 安装依赖
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
```

## 2) 启动
```bash
python app.py
```

浏览器访问：
- http://127.0.0.1:5000

## 3) 可选：限制上传大小
设置环境变量 `MAX_CONTENT_LENGTH`（单位：字节），例如 200MB：
```bash
export MAX_CONTENT_LENGTH=$((200*1024*1024))
python app.py
```

## 4) Docker
```bash
docker build -t pdf-merge-tool .
docker run --rm -p 5000:5000 pdf-merge-tool
```

## 5) 说明
- 对于需要密码的加密 PDF，本工具会提示失败（除非空密码可解）。
