FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi==0.165.0 uvicorn==0.54.0
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
