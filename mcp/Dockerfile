FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
