# Bot backend ke liye Docker image
FROM python:3.11-slim

WORKDIR /app

# requirements install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# code copy karo
COPY app.py sms_providers.py ./

# Port (Render/Railway/Koyeb default)
EXPOSE 8000

# Secrets environment se aate hain (.env yahan copy NAHI hota - deploy platform me set karte hain)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
