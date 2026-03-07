FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by gevent and pandas-ta
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create instance directory for SQLite
RUN mkdir -p backend/instance

EXPOSE 5050

# Run migrations then start the app
CMD ["sh", "-c", "flask db upgrade && python app.py"]
