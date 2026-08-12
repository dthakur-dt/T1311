# Root-level Dockerfile — Render/Koyeb/Railway ise root se utha lete hain
FROM python:3.11-slim

WORKDIR /app

# Backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Backend code (secrets .env se deploy platform pe aate hain, repo me nahi)
COPY backend/app.py backend/sms_providers.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
