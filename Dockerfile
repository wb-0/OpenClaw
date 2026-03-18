FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# 明确告知启动 app.py
CMD ["python", "app.py"]
